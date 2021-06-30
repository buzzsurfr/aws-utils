//
// rotate-access-key.go
//
//  Based on https://aws.amazon.com/blogs/security/how-to-rotate-access-keys-for-iam-users/

package main

import (
  "os"
  "os/exec"
  "log"
  "fmt"
  "time"
  "sort"
  "github.com/akamensky/argparse"
  "github.com/aws/aws-sdk-go/aws"
  "github.com/aws/aws-sdk-go/aws/credentials"
  "github.com/aws/aws-sdk-go/aws/session"
  "github.com/aws/aws-sdk-go/service/iam"
  "github.com/aws/aws-sdk-go/aws/awserr"
)

func main() {
  // Arguments
	parser := argparse.NewParser("rotate_access_keys", "Rotates IAM Access Keys")

	UserNamePtr := parser.String("", "user-name", &argparse.Options{Required: true, Help: "UserName of the AWS user"})
  AccessKeyIdPtr := parser.String("", "access-key-id", &argparse.Options{Required: false, Help: "Id of the Access key to replace"})
  ProfilePtr := parser.String("", "profile", &argparse.Options{Help: "Local Profile", Default: "default"})
  NoDeletePtr := parser.Flag("", "no-delete", &argparse.Options{Help: "Do not Delete old Access Key"})
  VerbosePtr := parser.Flag("v", "verbose", &argparse.Options{Help: "Verbose Logging"})

	// Parse input
	parser_err := parser.Parse(os.Args)
	if parser_err != nil {
    // In case of error print error and print usage
    // This can also be done by passing -h or --help flags
    fmt.Println(parser_err.Error())
    // fmt.Print(parser.Usage())
	}
  if *VerbosePtr {
    fmt.Printf("UserName:\t%v\nAccessKeyId:\t%v\nProfile:\t%v\nDelete:\t%v\n", *UserNamePtr, *AccessKeyIdPtr, *ProfilePtr, *NoDeletePtr)
  }

  // Create Session
  sess, sess_err := session.NewSession(&aws.Config{
    Region: aws.String("us-east-1"),
    Credentials: credentials.NewCredentials(&credentials.SharedCredentialsProvider{}),
  })
  if sess_err != nil {
    fmt.Println("Session error")
  }
  // fmt.Printf("Using access key %s.\n", credValue.AccessKeyID)

  // Create a IAM service client.
  iamSvc := iam.New(sess)

  listKeysResult, listKeysError := iamSvc.ListAccessKeys(&iam.ListAccessKeysInput{
    MaxItems: aws.Int64(5),
    UserName: aws.String(*UserNamePtr),
  })

  // Exit on error
  if listKeysError != nil {
    fmt.Println("Error", listKeysError)
    return
  }

  // Sort Access Keys (First key is oldest)
  sort.Slice(listKeysResult.AccessKeyMetadata, func(i, j int) bool {
    return (*listKeysResult.AccessKeyMetadata[i].CreateDate).Before(*listKeysResult.AccessKeyMetadata[j].CreateDate)
  })

  // Create New Access Key
  createKeyResult, createKeyError := iamSvc.CreateAccessKey(&iam.CreateAccessKeyInput{
    UserName: aws.String(*UserNamePtr),
  })
  if createKeyError != nil {
    if aerr, ok := createKeyError.(awserr.Error); ok {
        switch aerr.Code() {
        case iam.ErrCodeNoSuchEntityException:
            fmt.Println(iam.ErrCodeNoSuchEntityException, aerr.Error())
        case iam.ErrCodeLimitExceededException:
            fmt.Println(iam.ErrCodeLimitExceededException, aerr.Error())
        case iam.ErrCodeServiceFailureException:
            fmt.Println(iam.ErrCodeServiceFailureException, aerr.Error())
        default:
            fmt.Println(aerr.Error())
        }
    } else {
        // Print the error, cast err to awserr.Error to get the Code and
        // Message from an error.
        fmt.Println(createKeyError.Error())
    }
    return
  }
  fmt.Println(createKeyResult)
  // fmt.Printf("Access Key Id: %v\n", *createKeyResult.AccessKey.AccessKeyId)

  // Change awscli to use new access key
  aki_cmd := exec.Command("aws","--profile",*ProfilePtr,"configure","set","aws_access_key_id",*createKeyResult.AccessKey.AccessKeyId)
  aki_err := aki_cmd.Run()
	if aki_err != nil {
		log.Fatal(aki_err)
	}
  sak_cmd := exec.Command("aws","--profile",*ProfilePtr,"configure","set","aws_secret_access_key",*createKeyResult.AccessKey.SecretAccessKey)
  sak_err := sak_cmd.Run()
	if sak_err != nil {
		log.Fatal(sak_err)
	}

  // Create credential
  // creds := credentials.NewCredentials(&credentials.SharedCredentialsProvider{})

  // Pause
  time.Sleep(2 * time.Second)

  // Retrieve the credentials value
  sess.Config.Credentials.Expire()

  newListKeysResult, _ := iamSvc.ListAccessKeys(&iam.ListAccessKeysInput{
    MaxItems: aws.Int64(5),
    UserName: aws.String(*UserNamePtr),
  })
  fmt.Printf("Access Keys:\n%v", newListKeysResult)

  // Make old access key inactive (if old existed)
  // Command: aws iam update-access-key --access-key-id AKIA**************** --user-name {{AWS:UserName}} --status Inactive
  fmt.Println("UpdateAccessKey")
  _, updateAccessKeyError := iamSvc.UpdateAccessKey(&iam.UpdateAccessKeyInput{
    AccessKeyId: aws.String(*listKeysResult.AccessKeyMetadata[0].AccessKeyId),
    UserName: aws.String(*UserNamePtr),
    Status: aws.String("Inactive"),
  })
  if updateAccessKeyError != nil {
    if aerr, ok := updateAccessKeyError.(awserr.Error); ok {
        switch aerr.Code() {
        case iam.ErrCodeNoSuchEntityException:
            fmt.Println(iam.ErrCodeNoSuchEntityException, aerr.Error())
        case iam.ErrCodeLimitExceededException:
            fmt.Println(iam.ErrCodeLimitExceededException, aerr.Error())
        case iam.ErrCodeServiceFailureException:
            fmt.Println(iam.ErrCodeServiceFailureException, aerr.Error())
        default:
            fmt.Println(aerr.Error())
        }
    } else {
        // Print the error, cast err to awserr.Error to get the Code and
        // Message from an error.
        fmt.Println(updateAccessKeyError.Error())
    }
  }

  // Delete unless explicity specified not to in argument
  if *NoDeletePtr == false {
    fmt.Println("DeleteAccessKey")
    _, deleteAccessKeyError := iamSvc.DeleteAccessKey(&iam.DeleteAccessKeyInput{
      AccessKeyId: aws.String(*listKeysResult.AccessKeyMetadata[0].AccessKeyId),
      UserName:    aws.String(*UserNamePtr),
    })
    if deleteAccessKeyError != nil {
      if aerr, ok := deleteAccessKeyError.(awserr.Error); ok {
        switch aerr.Code() {
          case iam.ErrCodeNoSuchEntityException:
              fmt.Println(iam.ErrCodeNoSuchEntityException, aerr.Error())
          case iam.ErrCodeLimitExceededException:
              fmt.Println(iam.ErrCodeLimitExceededException, aerr.Error())
          case iam.ErrCodeServiceFailureException:
              fmt.Println(iam.ErrCodeServiceFailureException, aerr.Error())
          default:
              fmt.Println(aerr.Error())
        }
      } else {
        // Print the error, cast err to awserr.Error to get the Code and
        // Message from an error.
        fmt.Println(deleteAccessKeyError.Error())
      }
    }
  }
}
