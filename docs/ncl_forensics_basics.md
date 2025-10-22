# NCL Digital Forensics Guide

## Overview

Digital forensics challenges involve analyzing files, disk images, memory dumps, and other digital artifacts to find flags or understand what happened.

## File Analysis

### Basic File Identification

```bash
# File type
file suspicious.bin

# File strings
strings suspicious.bin | less
strings -n 8 suspicious.bin | grep -i flag

# Hexdump
hexdump -C suspicious.bin | less
xxd suspicious.bin | less

# Check file signature (magic bytes)
head -c 20 suspicious.bin | xxd
```

### Metadata Examination

**ExifTool:**
```bash
# View all metadata
exiftool image.jpg

# Check for hidden data in metadata
exiftool -a -u image.jpg
```

**File Carving:**
```bash
# Foremost
foremost -i disk.img -o output/

# Binwalk - find embedded files
binwalk suspicious.bin
binwalk -e suspicious.bin  # Extract

# Scalpel
scalpel disk.img -o output/
```

## Image Analysis

### Steganography

Hidden data in images.

**Common Tools:**

```bash
# Steghide (JPEG, BMP, WAV, AU)
steghide info image.jpg
steghide extract -sf image.jpg -p password

# Stegsolve (Java tool)
# Great for LSB analysis, color filters
java -jar stegsolve.jar

# zsteg (PNG & BMP)
zsteg image.png
zsteg -a image.png  # All checks

# Outguess
outguess -r image.jpg output.txt
```

**Manual Checks:**
```bash
# Check for hidden data at end of file
tail -c 1000 image.jpg | strings

# Look for ZIP/RAR signatures in image
binwalk image.jpg

# Check LSB
stegsolve (use filters and extract data)
```

**Online Tools:**
- Aperi'Solve: https://aperisolve.fr/
- StegOnline: https://stegonline.georgeom.net/

### Image Manipulation

```bash
# ImageMagick
convert image.jpg -resize 50% smaller.jpg
convert image.jpg -negate inverted.jpg

# Change color channels
convert image.jpg -channel R -separate red.jpg
```

## Archive Analysis

### ZIP Files

```bash
# List contents
unzip -l archive.zip

# Extract
unzip archive.zip

# Extract with password
unzip -P password archive.zip

# Check for extra data
zipinfo -v archive.zip

# Repair corrupted ZIP
zip -F broken.zip --out fixed.zip
```

### TAR Files

```bash
# Extract
tar -xvf archive.tar
tar -xzvf archive.tar.gz
tar -xjvf archive.tar.bz2

# List contents
tar -tvf archive.tar
```

## Memory Forensics

### Volatility Framework

Memory dump analysis tool.

**Common Commands:**

```bash
# Identify OS profile
volatility -f memory.dmp imageinfo

# List processes
volatility -f memory.dmp --profile=Win7SP1x64 pslist
volatility -f memory.dmp --profile=Win7SP1x64 pstree

# Network connections
volatility -f memory.dmp --profile=Win7SP1x64 netscan

# Command line history
volatility -f memory.dmp --profile=Win7SP1x64 cmdline

# Dump process
volatility -f memory.dmp --profile=Win7SP1x64 procdump -p 1234 -D output/

# Files in memory
volatility -f memory.dmp --profile=Win7SP1x64 filescan
volatility -f memory.dmp --profile=Win7SP1x64 dumpfiles -Q 0x... -D output/

# Registry hives
volatility -f memory.dmp --profile=Win7SP1x64 hivelist
volatility -f memory.dmp --profile=Win7SP1x64 printkey -K "Software\Microsoft\Windows\CurrentVersion\Run"

# Clipboard
volatility -f memory.dmp --profile=Win7SP1x64 clipboard

# Screenshots
volatility -f memory.dmp --profile=Win7SP1x64 screenshot -D output/
```

## Disk Forensics

### Autopsy / Sleuth Kit

GUI forensic tool for disk analysis.

**Features:**
- File system analysis
- Timeline creation
- Keyword search
- File recovery
- Registry analysis

**Basic Usage:**
1. Create case
2. Add disk image
3. Analyze file system
4. Search for artifacts

### FTK Imager

Disk imaging and analysis.

**Features:**
- Create disk images
- Browse file systems
- Export files
- View deleted files

## Log Analysis

### Common Log Locations

**Linux:**
- `/var/log/auth.log` - Authentication
- `/var/log/syslog` - System logs
- `/var/log/apache2/access.log` - Apache access
- `/var/log/apache2/error.log` - Apache errors
- `.bash_history` - Command history

**Windows:**
- `C:\Windows\System32\winevt\Logs\` - Event logs
- `Security.evtx` - Security events
- `System.evtx` - System events
- `Application.evtx` - Application events

### Analyzing Logs

```bash
# Search for keyword
grep -i "failed" /var/log/auth.log

# Count occurrences
grep -c "error" /var/log/syslog

# Show unique IPs
cat access.log | awk '{print $1}' | sort -u

# Filter by date/time
grep "Jan 15" /var/log/syslog

# Most frequent IPs
cat access.log | awk '{print $1}' | sort | uniq -c | sort -rn | head
```

## Registry Forensics (Windows)

### Registry Locations

- `HKEY_LOCAL_MACHINE\SOFTWARE` - Installed software
- `HKEY_CURRENT_USER\Software` - User settings
- `...\CurrentVersion\Run` - Startup programs
- `...\RecentDocs` - Recent documents

### Tools

**RegRipper:**
```bash
# Extract artifacts from registry hive
rip.pl -r NTUSER.DAT -f ntuser > output.txt
```

**Registry Explorer:**
GUI tool for browsing registry hives.

## File System Artifacts

### Windows

**Prefetch Files:**
- `C:\Windows\Prefetch\`
- Shows recently executed programs
- Filename format: `PROGRAM-HASH.pf`

**LNK Files:**
- Recent shortcuts
- Contain target path, timestamps
- Located in: `%APPDATA%\Microsoft\Windows\Recent\`

**USN Journal:**
- Tracks file system changes
- Can show deleted files

**$MFT (Master File Table):**
- Contains all file metadata
- Analyze with MFTExplorer

### Linux

**Recently Used:**
- `.bash_history`
- `.recently-used`
- Browser history databases

## Timeline Analysis

### Creating Timeline

**mactime (Sleuth Kit):**
```bash
# Create body file
fls -r -m C: disk.img > bodyfile

# Create timeline
mactime -b bodyfile -d > timeline.csv
```

### Analyzing Timeline

Look for:
- File creation times
- Modification times
- Access times
- Suspicious time patterns

## Common NCL Forensics Patterns

### 1. Strings in Files

```bash
# Basic strings
strings file.bin | grep -i flag

# Longer strings only
strings -n 10 file.bin

# Wide character strings (UTF-16)
strings -e l file.bin
```

### 2. Hidden Data in Images

1. Try `binwalk` first
2. Use `stegsolve` for visual analysis
3. Check metadata with `exiftool`
4. Try `zsteg` for PNG
5. Look for ZIP/RAR at end of file

### 3. Deleted Files

- Use Autopsy to browse disk image
- Check for file carving results
- Look in Recycle Bin / Trash

### 4. PDF Analysis

```bash
# PDF structure
pdfinfo document.pdf

# Extract streams
pdf-parser document.pdf

# JavaScript in PDF
peepdf -i document.pdf
```

### 5. Office Documents

Office files are ZIP archives!

```bash
# Unzip Word document
unzip document.docx -d extracted/

# Check for macros
olevba document.docm

# Analyze OLE files
oleid suspicious.doc
```

## Quick Analysis Workflow

1. **File Identification**
   ```bash
   file unknown.bin
   ```

2. **Strings Analysis**
   ```bash
   strings unknown.bin | grep -i flag
   ```

3. **Metadata Check**
   ```bash
   exiftool unknown.bin
   ```

4. **Signature Analysis**
   ```bash
   binwalk unknown.bin
   ```

5. **Hex Analysis**
   ```bash
   xxd unknown.bin | less
   ```

6. **Extract Embedded Files**
   ```bash
   binwalk -e unknown.bin
   foremost -i unknown.bin
   ```

## Useful One-Liners

```bash
# Find files modified in last 24 hours
find / -mtime -1 -type f 2>/dev/null

# Search for string in all files
grep -r "flag" /path/to/search

# Find SUID binaries
find / -perm -4000 -type f 2>/dev/null

# Find large files
find / -type f -size +100M 2>/dev/null

# File type statistics
file * | awk -F: '{print $2}' | sort | uniq -c

# Extract emails from file
grep -E -o "\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b" file.txt

# Extract IPs
grep -E -o "([0-9]{1,3}\.){3}[0-9]{1,3}" file.txt

# Extract URLs
grep -E -o "https?://[a-zA-Z0-9./?=_-]*" file.txt
```

## NCL Forensics Tips

1. **Start Simple**
   - `file` command first
   - Then `strings`
   - Check metadata
   - Look for obvious hiding spots

2. **Common Hiding Places**
   - End of files (after normal data)
   - Image LSB
   - File metadata (EXIF)
   - Alternate data streams (Windows)
   - Deleted space in file system

3. **Tools Priority**
   - Automated tools first (binwalk, foremost)
   - Then manual analysis
   - Specialized tools for specific formats

4. **Document Everything**
   - Take notes
   - Save commands used
   - Track file hashes

## Practice Resources

- DFIR CTF challenges
- Digital Corpora (forensic images)
- Forensics CTF challenges on CTFtime
- Autopsy sample images

## Quick Reference

| Task | Tool | Command |
|------|------|---------|
| File type | file | `file unknown` |
| Strings | strings | `strings file` |
| Metadata | exiftool | `exiftool image.jpg` |
| Hidden files | binwalk | `binwalk -e file` |
| Steganography | steghide | `steghide extract -sf image.jpg` |
| Memory | volatility | `volatility -f mem.dmp pslist` |
| Disk forensics | autopsy | GUI tool |
| File carving | foremost | `foremost -i disk.img` |

Remember: Forensics is methodical. Work systematically through your toolkit!

