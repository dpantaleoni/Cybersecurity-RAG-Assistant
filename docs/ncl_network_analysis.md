# NCL Network Analysis and Traffic Analysis

## Overview

Network analysis challenges in NCL involve examining network traffic, protocols, and packet captures to find flags or understand network behavior.

## Essential Tools

### Wireshark
The primary tool for packet analysis.

**Key Features:**
- Packet capture and analysis
- Protocol dissection
- Display filters
- Follow streams
- Export objects

**Common Display Filters:**
```
http                          # HTTP traffic only
tcp.port == 80               # Traffic on port 80
ip.addr == 192.168.1.1      # Specific IP
http.request.method == "POST" # HTTP POST requests
tcp contains "password"      # Packets containing "password"
dns                          # DNS traffic
ftp                          # FTP traffic
```

**Follow Stream:**
- Right-click packet → Follow → TCP/UDP/HTTP Stream
- See full conversation between client and server
- Great for reconstructing files or finding credentials

### tcpdump
Command-line packet capture tool.

```bash
# Capture on interface
tcpdump -i eth0

# Save to file
tcpdump -i eth0 -w capture.pcap

# Read from file
tcpdump -r capture.pcap

# Filter by port
tcpdump -i eth0 port 80

# Filter by host
tcpdump -i eth0 host 192.168.1.1

# Show ASCII content
tcpdump -A -r capture.pcap
```

### tshark
Command-line version of Wireshark.

```bash
# Read pcap file
tshark -r capture.pcap

# Apply display filter
tshark -r capture.pcap -Y "http"

# Extract HTTP objects
tshark -r capture.pcap --export-objects http,/tmp/objects

# Show specific fields
tshark -r capture.pcap -T fields -e ip.src -e ip.dst -e tcp.port
```

## Common Protocol Analysis

### HTTP/HTTPS Traffic

**What to Look For:**
- Usernames and passwords in POST requests
- API keys in headers or parameters
- File uploads/downloads
- Session cookies
- Hidden parameters in URLs

**Wireshark Filters:**
```
http.request.method == "POST"
http.request.uri contains "login"
http.cookie contains "session"
http.response.code == 200
```

**Extracting Files:**
- File → Export Objects → HTTP
- Save interesting files
- Check for hidden data in images, documents

### FTP Traffic

FTP sends credentials in plaintext!

**Wireshark Filters:**
```
ftp                           # All FTP traffic
ftp.request.command == "USER" # Username commands
ftp.request.command == "PASS" # Password commands
```

**Finding Credentials:**
1. Filter for FTP traffic
2. Look for USER and PASS commands
3. Follow TCP stream to see full session

### DNS Traffic

DNS can leak information and be used for data exfiltration.

**Wireshark Filters:**
```
dns
dns.qry.name contains "flag"
dns.flags.response == 0  # Queries only
dns.flags.response == 1  # Responses only
```

**What to Check:**
- Unusual domain names
- Long subdomain names (possible data exfil)
- DNS tunneling patterns

### SMTP Traffic

Email traffic can contain sensitive information.

**Wireshark Filters:**
```
smtp
smtp.data.fragment
```

**Follow TCP stream to read email content**

### Telnet Traffic

Like FTP, Telnet is unencrypted.

```
telnet
```

Follow TCP stream to see full terminal session including commands and credentials.

## Network Scanning Analysis

### Identifying Scans in Packet Captures

**Nmap SYN Scan:**
- Many SYN packets to different ports
- No ACK responses (stealth scan)

**Nmap Connect Scan:**
- Full TCP handshakes
- Multiple connections to different ports

**Nmap UDP Scan:**
- ICMP port unreachable responses

**Port Scan Detection Filter:**
```
tcp.flags.syn == 1 and tcp.flags.ack == 0
```

## Traffic Statistics

### Protocol Hierarchy
Statistics → Protocol Hierarchy
- See breakdown of protocols
- Identify unusual traffic

### Conversations
Statistics → Conversations
- See all conversations between hosts
- Sort by bytes to find bulk transfers

### Endpoints
Statistics → Endpoints
- See all IP addresses
- Identify top talkers

## Common NCL Network Patterns

### 1. Hidden Data in TCP/UDP Streams

**Method:**
- Right-click packet → Follow Stream
- Look for flags in conversation
- Check for base64 or hex encoded data

### 2. Data in ICMP Packets

Data can be hidden in ICMP ping payloads.

```
icmp
```

Check packet details → Data section

### 3. Malware Traffic

**Indicators:**
- Beaconing (regular intervals)
- Unusual ports
- Large data transfers
- Suspicious domains

### 4. Credential Harvesting

**Protocols to Check:**
- HTTP POST to login pages
- FTP (USER/PASS)
- Telnet
- SMTP AUTH
- POP3/IMAP

### 5. File Transfers

**Extract Files:**
- HTTP: File → Export Objects → HTTP
- FTP: Follow TCP stream, save raw data
- TFTP: File → Export Objects → TFTP
- SMB: File → Export Objects → SMB

## Advanced Techniques

### Decrypting SSL/TLS
If you have the server's private key:

1. Edit → Preferences → Protocols → TLS
2. RSA keys list → Add key file
3. Now encrypted traffic shows decrypted

### Following Streams

**TCP Stream:**
- Right-click → Follow → TCP Stream
- See full bidirectional conversation
- Great for protocols like HTTP, FTP, Telnet

**UDP Stream:**
- Similar to TCP
- Useful for DNS, DHCP, TFTP

### Carving Files from Network Traffic

```bash
# Using foremost
foremost -i capture.pcap -o output/

# Using binwalk
binwalk capture.pcap

# Using NetworkMiner (GUI tool)
# Can automatically extract files, credentials, etc.
```

## Useful tshark Commands for CTF

```bash
# Extract HTTP POSTs
tshark -r capture.pcap -Y "http.request.method == POST" -T fields -e http.file_data

# List all DNS queries
tshark -r capture.pcap -Y "dns.flags.response == 0" -T fields -e dns.qry.name

# Extract FTP credentials
tshark -r capture.pcap -Y "ftp.request.command == USER || ftp.request.command == PASS" -T fields -e ftp.request.arg

# Find all unique IP addresses
tshark -r capture.pcap -T fields -e ip.src -e ip.dst | sort -u

# Extract HTTP User-Agents
tshark -r capture.pcap -Y "http.user_agent" -T fields -e http.user_agent | sort -u
```

## NetworkMiner

Great for automatic analysis:
- Extracts files automatically
- Finds credentials
- Shows hosts and their details
- Reconstructs images
- Free and easy to use

## Quick Analysis Workflow

1. **Open pcap in Wireshark**
2. **Check Protocol Hierarchy** (Statistics menu)
   - See what protocols are present
3. **Look for Suspicious Protocols**
   - HTTP, FTP, Telnet, DNS
4. **Apply Filters**
   - http, ftp, dns, etc.
5. **Follow Streams**
   - Right-click interesting packets
6. **Export Objects**
   - File → Export Objects
7. **Check Statistics**
   - Conversations, Endpoints
8. **Search for Keywords**
   - Edit → Find Packet
   - Search for "flag", "password", "user", etc.

## Practice Resources

- Wireshark Sample Captures (wiki.wireshark.org)
- Malware-Traffic-Analysis.net
- DFIR.training
- NetworkMiner sample captures

Remember: Network analysis is about pattern recognition and knowing where to look. Start broad, then narrow down with filters!

