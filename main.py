#!/bin/python3

import json, csv
import boto3
from pprint import pprint
from datetime import datetime
import subprocess, os

#def lambda_handler(event, context):
print("---------------Script Starts-------------")
print("")

#-------------------Variable-------------

Bucket_region = os.getenv("Bucket_region")
Bucket_Name = os.getenv("Bucket_Name")
filename= os.getenv("filename")

#----------------------------------------
#defining file name
def date_on_filename(filename, file_extension):  
	date = str(datetime.now().date())
	return filename + "-" + date + "." + file_extension

report_filename = date_on_filename(filename, "csv")
print(f"output file name: {report_filename}")

#file path
filepath= "/tmp/" + report_filename
print(f"Output File Patch {filepath}")
print("")

#Collecting Account Number
sts_cli=boto3.client(service_name='sts', region_name="us-east-1")
responce_1=sts_cli.get_caller_identity()
account_number=responce_1.get("Account")
#--------------------------------------------

#--------------Manually update the dic.keys() to header_list if mismatch

header_list=['Region','OwnerID','Name', 'SnapshotId', 'Description', 'VolumeId', 'Capacity-GB', 'CreatedTime', 'WBS', 'Encrypted', 'KmsKeyId', 'Progress', 'State']
print(f"Header for CSV file = {header_list}")
print(" ")
# to add 50 Tag headers
for v in range(1,51):
    header_list.append(f'Tag{v}')
#--------------------------------------------
    #Collect all regions if needed
#--------------------------------------------
#-----------collect all region list into Regions
print("collecting all the regions name")

ec2_cli = boto3.client(service_name='ec2', region_name="us-east-1")    
responce=ec2_cli.describe_regions()
#pprint(responce['Regions'])
Regions=[]
for each in responce['Regions']:
    #print(each['RegionName'])
    Regions.append(each['RegionName'])    
print(f"Total {len(Regions)} regions")
print("")

#Regions=['us-east-1']
x=1 

#----------creating file with headder
print("Oppening the csv file to append each server details")
with open(filepath,'w') as csv_file:
#with open("outpu.csv",'w') as csv_file:
    Writer=csv.writer(csv_file)
    Writer.writerow(header_list)

    #revert the changes here
    print("Now going through each regions to check ec2 details")
    print("")
    for region in Regions:
        #print(region)
        #print(type(region))
        ec2_cli=boto3.client(service_name='ec2', region_name=region)

        all_snapshots=ec2_cli.describe_snapshots(OwnerIds=[account_number,],)
        #pprint(all_snapshots)
        #print(" ")
        for each in all_snapshots['Snapshots']:
            dic={'Region':region,'OwnerID':account_number,'Name': 'NA','SnapshotId':'NA','Description': 'NA','VolumeId':'NA','Capacity-GB':'NA',
            'CreatedTime':'NA','WBS': 'NA','Encrypted':'NA','KmsKeyId':'NA','Progress':'NA','State':'NA'}
            #print(each.items())
            #print(each.keys())
            #print(each.values())
            
            #print(each['Tags'])
            
            # collecting WBS and Name 
#            print(each.get('Tags'))
            if each.get('Tags') != None:
                for tags in each['Tags']:
                    #print(tags.values())
                    if tags['Key'] == 'Name':
                        #print("Yes, found Name-Tag")
                        #print(tags['Value'])
                        dic['Name']=tags['Value']
                    if tags['Key'] == 'WBS':
                        #print("Yes, found WBS-Tag")
                        dic['WBS']=tags['Value']
                b=1
                for tag in each['Tags']:
                    #print(each.values())
                    dic[f'Tag{b}']=list(tag.values())
                    b+=1
            
            if each.get('Description') != None:
                dic['Description']=each['Description']
            if each.get('Encrypted') != None:    
                dic['Encrypted']=each['Encrypted']
            if each.get('KmsKeyId') != None:    
                dic['KmsKeyId']=each['KmsKeyId']
            if each.get('Progress') != None:    
                dic['Progress']=each['Progress']

            if each.get('SnapshotId') != None:    
                dic['SnapshotId']=each['SnapshotId']
            if each.get('State') != None:    
                dic['State']=each['State']
            if each.get('VolumeId') != None:    
                dic['VolumeId']=each['VolumeId']
            if each.get('VolumeSize') != None:    
                dic['Capacity-GB']=each['VolumeSize']
           
            #creation time
            if each.get('StartTime') != None:    
                dic['CreatedTime']=each['StartTime'].strftime("%m/%d/%Y, %H:%M:%S")


                
            
            
            print(dic.keys())
            print(" ")
            print(dic)
            Writer.writerow(dic.values())
            print(f"\n------Snapshot {x} details been taken\n")
            x=x+1
            
        
            
#to check the what are the files exist under folder
#lscommand = subprocess.run(f"ls {filepath}", shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
lscommand = subprocess.run(f"ls {filepath}", shell=True, capture_output=True, text=True)
print(f"Output file Location:\n{lscommand.stdout}")



#transfer the file to s3
print(f"moving the file to S3 Bucket: {Bucket_Name}")
s3_cli=boto3.client(service_name='s3', region_name=Bucket_region)
#s3_cli.upload_file(filepath, Bucket_Name, report_filename)

#remove the file from container
#removefile=subprocess.run(f"rm -rfv {filepath}", shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
#print(f"Removed the output file from /tmp/ dir\n{removefile.stdout.decode('utf-8')}")
print(" ")
print("-----------------Script Ends--------------------")
