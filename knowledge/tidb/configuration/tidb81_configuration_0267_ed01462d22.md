# Create AWS interface endpoint, register connection, enable private DNS, and connect

## Knowledge Metadata

- Knowledge Type: `configuration`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-cloud/set-up-private-endpoint-connections.md`
- Source Title: `Connect to a TiDB Cloud Dedicated Cluster via AWS PrivateLink`
- Source Heading Path: `Connect to a TiDB Cloud Dedicated Cluster via AWS PrivateLink > Set up a private endpoint connection and connect to your cluster > Step 2. Create an AWS interface endpoint | Connect to a TiDB Cloud Dedicated Cluster via AWS PrivateLink > Set up a private endpoint connection and connect to your cluster > Step 3. Create a private endpoint connection | Connect to a TiDB Cloud Dedicated Cluster via AWS PrivateLink > Set up a private endpoint connection and connect to your cluster > Step 4. Enable private DNS | Connect to a TiDB Cloud Dedicated Cluster via AWS PrivateLink > Set up a private endpoint connection and connect to your cluster > Step 5. Connect to your TiDB cluster`
- Source Line Ranges: `66-184`
- Source Scope: `cloud`
- Primary Component: `cloud`
- Related Components: `shared`
- Topic Tags: `aws-cli`, `aws-console`, `interface-endpoint`, `vpc-endpoint`, `private-dns`, `security-group`, `connection-status`, `network-access`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_configuration_0267_ed01462d22`
- Source ID: `tidb-docs-8.1:tidb-cloud/set-up-private-endpoint-connections.md#step-2-create-an-aws-interface-endpoint`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `f158feefb33c6192a92a1551baea92b2321ec080f83b631b565bd1ac60af15f0`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-cloud/set-up-private-endpoint-connections#step-2-create-an-aws-interface-endpoint
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-cloud/set-up-private-endpoint-connections.md

## Retrieval Guidance

- Use When: Use this chunk when you need the exact AWS interface endpoint creation flow, private endpoint registration, private DNS enablement, and final connection status steps for a TiDB Cloud Dedicated cluster via AWS PrivateLink.
- Retrieval Keywords: aws ec2 create-vpc-endpoint, aws ec2 modify-vpc-endpoint --private-dns-enabled, TiDB Private Link Service is ready, Create AWS Private Endpoint Connection, VPC endpoint ID, AWS interface endpoint, Endpoint services that use NLBs and GWLBs, Verify service, Security groups, Port 4000, Networking page, Project Settings > Network Access, System Checking, Active, Connect With, connection string
- Follow-up Guidance: It also notes that if connectivity fails, the AWS VPC endpoint security group might not be properly set and refers to the troubleshooting FAQ.
- Classification Note: This is classified as configuration because the content provides the concrete AWS CLI commands, AWS console fields, TiDB Cloud console pages, and connection-state checks used to complete private endpoint setup.

## Official Source Content

### Step 2. Create an AWS interface endpoint

> **Note:**
>
> For each TiDB Cloud Dedicated cluster created after March 28, 2023, the corresponding endpoint service is automatically created 3 to 4 minutes after the cluster creation.

If you see the `TiDB Private Link Service is ready` message, the corresponding endpoint service is ready. You can provide the following information to create the endpoint.

1. Fill in the **Your VPC ID** and **Your Subnet IDs** fields. You can find these IDs from your [AWS Management Console](https://console.aws.amazon.com/). For multiple subnets, enter the IDs separated by spaces.
2. Click **Generate Command** to get the following endpoint creation command.

    ```bash
    aws ec2 create-vpc-endpoint --vpc-id ${your_vpc_id} --region ${your_region} --service-name ${your_endpoint_service_name} --vpc-endpoint-type Interface --subnet-ids ${your_application_subnet_ids}
    ```

Then, you can create an AWS interface endpoint either using the AWS CLI or using the [AWS Management Console](https://aws.amazon.com/console/).

<div label="Use AWS CLI">

To use the AWS CLI to create a VPC interface endpoint, perform the following steps:

1. Copy the generated command and run it in your terminal.
2. Record the VPC endpoint ID you just created.

> **Tip:**
>
> - Before running the command, you need to have AWS CLI installed and configured. See [AWS CLI configuration basics](https://docs.aws.amazon.com/cli/latest/userguide/cli-configure-quickstart.html) for details.
>
> - If your service is spanning across more than three availability zones (AZs), you will get an error message indicating that the VPC endpoint service does not support the AZ of the subnet. This issue occurs when there is an extra AZ in your selected region in addition to the AZs where your TiDB cluster is located. In this case, you can contact [PingCAP Technical Support](https://docs.pingcap.com/tidbcloud/tidb-cloud-support).

</div>
<div label="Use AWS Console">

To use the AWS Management Console to create a VPC interface endpoint, perform the following steps:

1. Sign in to the [AWS Management Console](https://aws.amazon.com/console/) and open the Amazon VPC console at [https://console.aws.amazon.com/vpc/](https://console.aws.amazon.com/vpc/).
2. Click **Endpoints** in the navigation pane, and then click **Create Endpoint** in the upper-right corner.

    The **Create endpoint** page is displayed.

    ![Verify endpoint service](/media/tidb-cloud/private-endpoint/create-endpoint-2.png)

3. In the **Endpoint settings** area, fill in a name tag if needed, and then select the **Endpoint services that use NLBs and GWLBs** option.
4. In the **Service settings** area, enter the service name `${your_endpoint_service_name}` from the generated command (`--service-name ${your_endpoint_service_name}`).
5. Click **Verify service**.
6. In the **Network settings** area, select your VPC in the drop-down list.
7. In the **Subnets** area, select the availability zones where your TiDB cluster is located.

    > **Tip:**
    >
    > If your service is spanning across more than three availability zones (AZs), you might not be able to select AZs in the **Subnets** area. This issue occurs when there is an extra AZ in your selected region in addition to the AZs where your TiDB cluster is located. In this case, contact [PingCAP Technical Support](https://docs.pingcap.com/tidbcloud/tidb-cloud-support).

8. In the **Security groups** area, select your security group properly.

    > **Note:**
    >
    > Make sure the selected security group allows inbound access from your EC2 instances on Port 4000 or a customer-defined port.

9. Click **Create endpoint**.

</div>
### Step 3. Create a private endpoint connection

1. Go back to the TiDB Cloud console.
2. On the **Create AWS Private Endpoint Connection** page, enter your VPC endpoint ID.
3. Click **Create Private Endpoint Connection**.

> **Tip:**
>
> You can view and manage private endpoint connections on two pages:
>
> - Cluster-level **Networking** page: switch to your target cluster using the combo box in the upper-left corner, and then click **Settings** > **Networking** in the left navigation pane.
> - Project-level **Network Access** page: switch to your target project using the combo box in the upper-left corner, and then click **Project Settings** > **Network Access** in the left navigation pane.
### Step 4. Enable private DNS

Enable private DNS in AWS. You can either use the AWS CLI or the AWS Management Console.

<div label="Use AWS CLI">

To enable private DNS using your AWS CLI, copy the following `aws ec2 modify-vpc-endpoint` command from the **Create Private Endpoint Connection** page and run it in your AWS CLI.

```bash
aws ec2 modify-vpc-endpoint --vpc-endpoint-id ${your_vpc_endpoint_id} --private-dns-enabled
```

Alternatively, you can find the command on the **Networking** page of your cluster. Locate the private endpoint and click **...*** > **Enable DNS** in the **Action** column.

</div>
<div label="Use AWS Console">

To enable private DNS in your AWS Management Console:

1. Go to **VPC** > **Endpoints**.
2. Right-click your endpoint ID and select **Modify private DNS name**.
3. Select the **Enable for this endpoint** check box.
4. Click **Save changes**.

    ![Enable private DNS](/media/tidb-cloud/private-endpoint/enable-private-dns.png)

</div>
### Step 5. Connect to your TiDB cluster

After you have accepted the private endpoint connection, you are redirected back to the connection dialog.

1. Wait for the private endpoint connection status to change from **System Checking** to **Active** (approximately 5 minutes).
2. In the **Connect With** drop-down list, select your preferred connection method. The corresponding connection string is displayed at the bottom of the dialog.
3. Connect to your cluster with the connection string.

> **Tip:**
>
> If you cannot connect to the cluster, the reason might be that the security group of your VPC endpoint in AWS is not properly set. See [this FAQ](#troubleshooting) for solutions.
