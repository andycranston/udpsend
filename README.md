# udpsend

Utility to construct and send UDP packets for network daemon testing

## Prerequsites

You will need:

+ UNIX/Linux or Windows
+ Python 3 (tested on version 3.7.2)

## Quick start

The `udpsend.py` Python program reads a file (by default `udpsend.txt`)
and builds a network packet and then sends it to a network host on a
specified port. It can optionally wait for a response packet and display
the bytes in the response packet.

For example create a `udpsend.txt` file with the following content:

```
host 10.1.1.13
port 69
0x0001 'file' 0 'octet' 0
show
send
receive
```

Change the IPx4 address `10.1.1.13` to the IP address of a TFTP server
on your network.

Now run:

```
python udpsend.py
```

You might well get output similar to:

```
> 0000 : 00 01 66 69 6C 65 00 6F 63 74 65 74 00             ??file?octet?
< 0000 : 00 05 00 01 46 69 6C 65 20 6E 6F 74 20 66 6F 75    ????File not fou
< 0010 : 6E 64 00                                           nd?
```

What has happened here is that a TFTP read request for a file called
`file` to be transferred in binary format has been sent to a host
with IP address `10.1.1.5` on the well known TCP/IP port number `69`
for TFTP requests. The response packet indicates that the file called
`file` was not found on the TFTP server.

The output packet is shown as:

```
> 0000 : 00 01 66 69 6C 65 00 6F 63 74 65 74 00             ??file?octet?
```

and the response packet is show as:

```
< 0000 : 00 05 00 01 46 69 6C 65 20 6E 6F 74 20 66 6F 75    ????File not fou
< 0010 : 6E 64 00                                           nd?
```

As an experiment try changing the line:

```
0x0001 'file' 0 'octet' 0
```

in the `udpsend.txt` file to:

```
0x0001 'file' 0 'stream' 0
```

and run the program again and observe the content of the response packet.

## Command line option `-f` / `--file`

The optional command line option `--file` (short form `-f`) can be used
to specify a different packet specification file. For example if the
packet specification is in a file called `px2firmware.txt` then run the
`udpsend.py` program as follows:

```
python udpsend.py --file px2firmware.txt
```

or with the short form:

```
python udpsend.py -f px2firmware.txt
```

## Packet specification file

The `udpsend.txt` packet specification file (or the file specified after
the `--file`/`-f` command line option) contains lines which fall into
one of the following type:

+ A line that begins with the '#' character
+ Blank lines (or lines containing just spaces and/or tab characters)
+ Command lines
+ Data lines

A line beginning with the '#' character is regarded as a comment and can
be used to document the content of the file. It can also be used as a
handy way to 'comment out' command and data lines during the development
of the packet specification file. Comments are ignored by the `udpsend.py`
program.

Blank lines are ignored by the `udpsend.py` program.

Command lines contain a command with optional arguments.

Data lines contain text that represents the bytes of data that are to
be used to build the packet.

## Basic commands

The basic commands are now documented.

## Command 'host'

The `host` command expects one argument which is the hostname or IPv4
address of the host that the packet is to be sent to. Examples:

```
host swstore
```

```
host nserv.example.com
```

```
host 10.1.1.5
```

## Command `port`

The `port` command expects one argument which is the port number to send
the packet to.  For example:

```
port 161
```

would send the packet to port 161 which is the well known port number
for SNMP (Simple Network Management Protocol) queries.

## Command `show`

The `show` command does not require any arguments. It displays the
current packet.

For example if the current packet consisted of the four byte values 0x04,
0x41, 0x63, 0xC9 then the show command would produce the following output:

```
> 0000 : 04 41 63 C9                                        ?Ac?
```

If the current packet does not yet have any bytes in it the `show`
command will display:

```
> <empty packet>
```

## Command `send`

The `send` command does not require any arguments. It sends the current
packet to the host specified by the `host` command using the port number
specified by the `port` command.

## Command `receive`

The `receive` command does not require any arguments. It waits for a
packet from the host specified by the `host` command on the port number
specified by the `port` command.  If no packet is received within a time
out period a message similar to:

```
udpsend.py: timeout on receive packet - waited 2.0 seconds
```

will be displayed.

If a packet is received the bytes in the packet will be displayed. An
example output from the `receive` command might look like:

```
< 0000 : 00 05 00 01 46 69 6C 65 20 6E 6F 74 20 66 6F 75    ????File not fou
< 0010 : 6E 64 00                                           nd?
```

## Data lines

Data lines contain text representations of the byte data that is
to be added to a packet. Each data line can have one or more text
representations on it.  One packet specification file can contain multiple
data lines.

The order that data lines appear in the packet specification file matters
as does the order of each text representation on a particular data line.

The simplest text representation is a positive integer number in the
range 0 to 255 inclusive. This number represents a single byte to be
added to the packet. For example:

```
0
```

would add a byte with value zero to the packet.

A hexadecimal byte can be represented with the string '0x' immediately
followed by the two hexadecimal digits making up the byte. For example:

```
0xC9
```

would add a byte with decimal value 209 to the packet.

If more that one hexadecimal byte is to be added this shorthand can
be used:

```
0xC90140
```

which would added the three decimal numbers 209, 1 and 64 to the packet.

Note that the hexadecimal digits 'A' to 'F' inclusive can be specified
in either upper or lower case.

If byte values representing a string need to be added then use this form:

```
'Name'
```

The characters inside the single quote characters (') are converted to
the decimal ASCII code byte value and added to the packet.

You can also use double quote characters ("):

```
"Name"
```

They are equivalent.

ATTENTION: you cannot have spaces or tab characters inside the quote
characters. To encode the string "My Name" then this would be one way:

```
'My' 32 'Name'
```

as the decimal value 32 is the ASCII code byte value of a space character.

## Additional commands

As well as the basic commands:

+ `host`
+ `port`
+ `show`
+ `send`
+ `receive`

there are additional commands which are now documented.

## Command `timeout`

The `timeout` command requires one argument which is a positive floating
point number which sets how long the `receive` command is to wait for a
response. By default the timeout is 2.0 seconds. In some cases you may
want a different timeout value. For example:

```
timeout 5.5
```

would make the `receive` command wait 5 and a half seconds for a response.

## Command `null`

The `null` command does not require any arguments. It sets the current
packet to have no bytes.  It allows one packet to be built and sent and
then a second packet built and sent. For example in this segment of a
packet specification file:

```
data 'red'
send
receive
null
data 'green'
send
receive
```

a packet with the string 'red' is sent and then a second packet is built
with the string 'green' which is sent next.

## Command `fill`

The fill command allows data to be added to the packet multiple times. For
example to add 200 bytes of value zero use:

```
fill 200 0
```

You are not limited to just a single byte. This more complicated examaple:

```
fill 10 0x04 7 'private'
```

will fill the packet with 10 lots of:

```
0x04 7 'private'
```

which would be 10 lots of the following hexadecimal byte values:

```
0x04 0x07 0x70 0x72 0x69 0x76 0x61 0x74 0x65
```

## Command `prepend`

By default when data values are added to the packet they are added to the
end of the packet.  Sometimes it makes more sense to build the packet
"back to front". By using the `prepend` command all subsequent data
lines are added to the front of the packet. Here is an example:

```
prepend
'password'
8
0x04
show
```

This results in:

```
> 0000 : 04 08 70 61 73 73 77 6F 72 64                      ??password
```

SNMP packets are usually easier to build this way. Infact see the example
packet definition file:

```
px2firmware.txt
```

in the repository.

The `prepend` command does not require any arguments.

## Command `append`

The `append` command does not require any arguments. It cause data in
data lines to be added to the end of the packet. This is the default
action so the `append` command is sometime seen after a `prepend`
command in a packet definition file. An example:

```
prepend
'token'
5
0xFF
append
'#EOF#'
0
show
```

would display:

```
> 0000 : FF 05 74 6F 6B 65 6E 23 45 4F 46 23 00             ??token#EOF#?
```

## Command `length-1byte`

The `length-1byte` command adds a single byte to the packet. If the mode
is `append` the byte gets added to the end of the packet. If the mode is
`prepend` the byte is added to the beginning of the packet.

The value of the byte is the current length of the packet.

NOTE: the packet must currently be less than of equal to 255 bytes in
length. The `udpsend.py` program should probably check this but currently
does not.

The `length-1byte` is useful when used with `prepend` when building simple SNMP packages. For example:

```
prepend
# SNMP null
0x05 0
# SNMP OID 1.3.6.1.2.1.1.3.0
0x06 8 0x2B 6 1 2 1 1 3 0
# SNMP variable binding sequence
length-1byte
0x30
show
```

Will build a packet as follows:

```
> 0000 : 30 0C 06 08 2B 06 01 02 01 01 03 00 05 00          0???+?????????
```

If we change the input to:

```
prepend
# SNMP null
0x05 0
# SNMP variable binding sequence
length-1byte
0x30
show
```

we now get:

```
000 : 30 02 05 00                                        0???
```

For a better example of this look at the `px2firmware.txt` file.




## Commands `alias` and `aliases`

If you do not like the built names for the commands you can create
aliases for them with the `alias` command. The `alias` command takes
two arguments. The first is the name for the alias and the second is the
name of an existing command. For example to save typing "show" for the
`show` command and instead type "s" try:

```
alias s show
'moredata'
s
```

This should give:

```
> 0000 : 73 6F 6D 65 64 61 74 61                            somedata
```

To see which aliases are currently defined use the `aliases` command. It
does not require any arguments. For example:

```
alias s show
aliases
```

would display:

```
s => show
```

## Limitations

The `udpsend.py` command is only for IPv4 hosts and addresses.

It also only sends and receives UDP packets.

The maximum size of packet that can be built, sent or received is 1024000
but this limit can be changed by editing the line:

```
MAX_PACKET_SIZE = 1024000
```

in the `udpsend.py` file. However, if you need to send packets this big
or bigger then `udpsend.py` is probably not the best tool to be using
for your purposes.

## Contact the author

The `udpsend.py` program, this documentation and the example packet
definition files in this repository were written by me, Andy Cranston.

If you would like to get in touch then you can send me email:

```
andy [at] cranstonhub [dot] com
```

or find me on LinkedIn.com and send me a connection request.

----------------
End of README.md
