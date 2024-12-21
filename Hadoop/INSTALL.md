# Windows installation

### Prerequisites 

JAVA: 
Java SE Development Kit 8u351 https://www.oracle.com/java/technologies/javase/javase8u211-later-archive-downloads.html
- Windows x64 Installer jdk-8u351-windows-x64.exe https://www.oracle.com/java/technologies/javase/javase8u211-later-archive-downloads.html#license-lightbox

HADOOP: hadoop-3.2.4 https://hadoop.apache.org/release/3.2.4.html

SPARK: spark-3.5.3-bin-hadoop3 https://spark.apache.org/downloads.html

The Java installer will install the jdk in C:\Program Files\Java\jdk1.8.0_351 automatically, while the JRE destination can be changed. The Hadoop and Spark files can be extracted to any folder, but it is recommended to extract them to the root of the disk to avoid long paths.

### Folder Structure

All folder and files names cannot include spaces because of Hadoop specifications.

C:
- Java
- - jre1.8.0_351
- - - jdk1.8.0_351
- Hadoop
- - hadoop-3.2.4
- Spark
- - spark-3.5.3-bin-hadoop3

### Environment Variables
- CLASSPATH $\rightarrow$ .;C:\Java\jre1.8.0_351\jdk1.8.0_351\bin;
- JAVA_HOME $\rightarrow$ C:\Java\jre1.8.0_351\jdk1.8.0_351
- HADOOP_HOME $\rightarrow$ C:\Hadoop\hadoop-3.3.6
- SPARK_HOME $\rightarrow$ C:\Spark\spark-3.5.3-bin-hadoop3
- Path
- - %JAVA_HOME%\bin
- - %HADOOP_HOME%\bin
- - %HADOOP_HOME%\sbin
- - %SPARK_HOME%\bin

### Check if paths are correct

using cmd
```shell 
> java -version
java version "1.8.0_351"
Java(TM) SE Runtime Environment (build 1.8.0_351-b10)
Java HotSpot(TM) 64-Bit Server VM (build 25.351-b10, mixed mode)
```

```shell 
> spark-shell --version
Welcome to
      ____              __
     / __/__  ___ _____/ /__
    _\ \/ _ \/ _ `/ __/  '_/
   /___/ .__/\_,_/_/ /_/\_\   version 3.5.3
      /_/

Using Scala version 2.12.18, OpenJDK Client VM, 1.8.0_432
Branch HEAD
Compiled by user haejoon.lee on 2024-09-09T05:20:05Z
Revision 32232e9ed33bb16b93ad58cfde8b82e0f07c0970
Url https://github.com/apache/spark
Type --help for more information.
```

### Hadoop Configuration

Inside the folder %HADOOP_HOME%\etc\hadoop change the following files:

#### core-site.xml

```xml
<configuration>
  <property>
    <name>fs.defaultFS</name>
    <value>hdfs://localhost:9000</value>
  </property>
</configuration>
``` 

#### mapred-site.xml
```xml
<configuration>
  <property>
    <name>mapreduce.framework.name</name>
    <value>yarn</value>
  </property>
</configuration>
```

#### hdfs-site.xml
```xml
<configuration>
  <property>
    <name>dfs.replication</name>
    <value>1</value>
  </property>
  <property>
    <name>dfs.namenode.name.dir</name>
    <value>file:///C:/Hadoop/hadoop-3.2.4/data/namenode</value>
  </property>
  <property>
    <name>dfs.datanode.data.dir</name>
    <value>file:///C:/Hadoop/hadoop-3.2.4/data/datanode</value>
  </property>
</configuration>
```

#### httpfs-site.xml
```xml
<configuration>
  <property>
    <name>dfs.replication</name>
    <value>1</value>
  </property>
  <property>
    <name>dfs.namenode.name.dir</name>
    <value>C:\Hadoop\hadoop-3.2.4\data\namenode</value>
  </property>
  <property>
    <name>dfs.datanode.name.dir</name>
    <value>C:\Hadoop\hadoop-3.2.4\data\datanode</value>
  </property>
</configuration>
```

#### yarn-site.xml
```xml
<configuration>
  <property>
    <name>yarn.nodemanager.aux-services</name>
    <value>mapreduce_shuffle</value>
  </property>
  <property>
    <name>yarn.nodemanager.auxservices.mapreduce.shuffle.class</name>  
    <value>org.apache.hadoop.mapred.ShuffleHandler</value>
  </property>
</configuration>
```

#### Create directories

```shell
> mkdir %HADOOP_HOME%\data\namenode
> mkdir %HADOOP_HOME%\data\datanode
```

#### Test Hadoop

```shell
> hadoop version
Hadoop 3.3.6
Source code repository https://github.com/apache/hadoop.git -r 1be78238728da9266a4f88195058f08fd012bf9c
Compiled by ubuntu on 2023-06-18T08:22Z
Compiled on platform linux-x86_64
Compiled with protoc 3.7.1
From source with checksum 5652179ad55f76cb287d9c633bb53bbd
This command was run using /C:/Hadoop/hadoop-3.3.6/share/hadoop/common/hadoop-common-3.3.6.jar
```

#### Patch with winutils

Possible sources:
- https://github.com/cdarlint/winutils

[comment]: https://github.com/steveloughran/winutils

clone the repository 
```shell
git clone https://github.com/cdarlint/winutils.git
```

- copy the files from winutiles/hadoop3.2.2/bin to %HADOOP_HOME%\bin

- copy the hadoop.dll to Windows\System32

if this does not work, use Hadoop_3_2_4_bin.zip from the repository

- double click winutils.exe

If an error pops up, install msvcr120.dll and msvc-170.dll to Windows\System32

#### copy yarn timeline files

```shell
copy %HADOOP_HOME%\share\hadoop\yarn\timelineservice\*.jar %HADOOP_HOME%\share\hadoop\yarn\
```

#### Boot HDFS

```shell
start-dfs.cmd
```
The HDFS should be running on http://localhost:9870
If you have problems with an occupied port: 
```shell
netstat -ano | findstr :9000
```
Then identify the process which is using that door, and put his PID here:
```shell
tasklist | findstr 1234
```
And retry the command above to start hdfs.

#### Boot YARN

```shell
start-yarn.cmd
```
The YARN should be running on http://localhost:8088

#### Test HDFS

```shell
hdfs dfs -mkdir /test
hadoop dfs -put ml-latest-small\ratings.csv \test\
hadoop dfs -put ml-latest-small\movies.csv \test\
hdfs dfs -ls /
```
