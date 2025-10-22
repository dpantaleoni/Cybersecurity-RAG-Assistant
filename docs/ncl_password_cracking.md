# NCL Password Cracking Guide

## Overview

Password cracking challenges test your ability to recover passwords from hashes, encrypted files, or by brute-forcing authentication systems.

## Hash Identification

First, identify the hash type:

### Common Hash Formats

| Hash Type | Length | Example |
|-----------|--------|---------|
| MD5 | 32 hex chars | 5f4dcc3b5aa765d61d8327deb882cf99 |
| SHA-1 | 40 hex chars | 5baa61e4c9b93f3f0682250b6cf8331b7ee68fd8 |
| SHA-256 | 64 hex chars | 5e884898da28047151d0e56f8dc6292773603d0d6aabbdd62a11ef721d1542d8 |
| SHA-512 | 128 hex chars | b109f3bbbc244eb82441917ed06d618b9008dd09b3befd1b5e07394c706a8bb980b1d7785e5976ec049b46df5f1326af5a2ea6d103fd07c95385ffab0cacbc86 |
| NTLM | 32 hex chars | 8846f7eaee8fb117ad06bdd830b7586c |
| bcrypt | Starts with $2a$, $2b$, or $2y$ | $2a$10$N9qo8uLOickgx2ZMRZoMye |

### Hash Identification Tools

```bash
# hash-identifier
hash-identifier

# hashid
hashid 5f4dcc3b5aa765d61d8327deb882cf99

# Online: https://hashes.com/en/tools/hash_identifier
```

## Tools

### Hashcat

The fastest password cracker (GPU-accelerated).

**Common Hash Modes:**
```bash
# MD5
hashcat -m 0 hashes.txt wordlist.txt

# SHA-1
hashcat -m 100 hashes.txt wordlist.txt

# SHA-256
hashcat -m 1400 hashes.txt wordlist.txt

# NTLM
hashcat -m 1000 hashes.txt wordlist.txt

# bcrypt
hashcat -m 3200 hashes.txt wordlist.txt

# MD5crypt (Linux)
hashcat -m 500 hashes.txt wordlist.txt
```

**Attack Modes:**
```bash
# Dictionary attack
hashcat -m 0 -a 0 hash.txt wordlist.txt

# Combinator attack
hashcat -m 0 -a 1 hash.txt wordlist1.txt wordlist2.txt

# Brute force
hashcat -m 0 -a 3 hash.txt ?a?a?a?a?a?a

# Hybrid (wordlist + mask)
hashcat -m 0 -a 6 hash.txt wordlist.txt ?d?d?d
```

**Masks:**
- `?l` = lowercase letter
- `?u` = uppercase letter
- `?d` = digit
- `?s` = special character
- `?a` = all characters

**Examples:**
```bash
# 6-character password with letters and digits
hashcat -m 0 -a 3 hash.txt ?a?a?a?a?a?a

# Word followed by 2 digits (e.g., password12)
hashcat -m 0 -a 6 hash.txt rockyou.txt ?d?d

# Show cracked passwords
hashcat -m 0 hash.txt --show
```

### John the Ripper

Versatile password cracker, good for complex formats.

```bash
# Basic usage
john hashes.txt

# Specify wordlist
john --wordlist=/usr/share/wordlists/rockyou.txt hashes.txt

# Specify format
john --format=Raw-MD5 hashes.txt

# Show cracked passwords
john --show hashes.txt

# Incremental mode (brute force)
john --incremental hashes.txt

# Create custom wordlist with rules
john --wordlist=wordlist.txt --rules hashes.txt
```

**Common Formats:**
- `Raw-MD5`
- `Raw-SHA1`
- `Raw-SHA256`
- `NT` (NTLM)
- `bcrypt`
- `zip`
- `rar`

### CrackStation

Online hash lookup (rainbow tables).

URL: https://crackstation.net/

**Use for:**
- Quick lookups of common passwords
- MD5, SHA-1, SHA-256, NTLM
- Pre-computed rainbow tables

### Online Hash Databases

- https://hashes.com/
- https://md5decrypt.net/
- https://hashkiller.io/

## Wordlists

### Common Wordlists

```bash
# RockYou (most common)
/usr/share/wordlists/rockyou.txt

# SecLists
/usr/share/seclists/Passwords/

# Common passwords
/usr/share/wordlists/common.txt

# Download rockyou
wget https://github.com/brannondorsey/naive-hashcat/releases/download/data/rockyou.txt
```

### Creating Custom Wordlists

**CeWL - Web Scraper:**
```bash
# Create wordlist from website
cewl http://target.com -w wordlist.txt -d 2
```

**Crunch - Generate Wordlists:**
```bash
# Generate all 4-digit combinations
crunch 4 4 0123456789 -o wordlist.txt

# Generate 6-8 character passwords with lowercase
crunch 6 8 abcdefghijklmnopqrstuvwxyz -o wordlist.txt

# Pattern-based generation (@ = lowercase, , = uppercase, % = digit)
crunch 8 8 -t pass%%%% -o wordlist.txt
```

## Password Protected Files

### ZIP Files

```bash
# John the Ripper
zip2john encrypted.zip > hash.txt
john hash.txt

# fcrackzip
fcrackzip -u -D -p rockyou.txt encrypted.zip
```

### RAR Files

```bash
# John the Ripper
rar2john encrypted.rar > hash.txt
john hash.txt
```

### PDF Files

```bash
# John the Ripper
pdf2john encrypted.pdf > hash.txt
john hash.txt

# pdfcrack
pdfcrack -f encrypted.pdf -w rockyou.txt
```

### Office Documents

```bash
# LibreOffice/OpenOffice
office2john document.docx > hash.txt
john hash.txt
```

### SSH Keys

```bash
# Convert to hash
ssh2john id_rsa > hash.txt
john hash.txt
```

## Linux Password Cracking

### /etc/shadow Format

```
username:$6$salt$hash:lastchanged:min:max:warn:inactive:expire
```

**Hash Types:**
- `$1$` = MD5
- `$5$` = SHA-256
- `$6$` = SHA-512
- `$2a$` / `$2y$` = bcrypt

### Unshadowing

```bash
# Combine /etc/passwd and /etc/shadow
unshadow passwd.txt shadow.txt > unshadowed.txt

# Crack with John
john unshadowed.txt
```

## Windows Password Cracking

### SAM Database

**Extract hashes:**
```bash
# Using samdump2
samdump2 SYSTEM SAM > hashes.txt

# Using secretsdump (Impacket)
secretsdump.py -sam SAM -system SYSTEM LOCAL
```

**Crack NTLM hashes:**
```bash
hashcat -m 1000 ntlm_hashes.txt rockyou.txt
```

## Advanced Techniques

### Rule-Based Attacks

John and Hashcat support rules to mutate wordlist entries.

**Common Rules:**
- Append digits: `password` → `password1`, `password123`
- Capitalize: `password` → `Password`
- Leet speak: `password` → `p@ssw0rd`
- Reverse: `password` → `drowssap`

**Hashcat with rules:**
```bash
hashcat -m 0 hash.txt wordlist.txt -r /usr/share/hashcat/rules/best64.rule
```

**John with rules:**
```bash
john --wordlist=wordlist.txt --rules hashes.txt
```

### Mask Attacks

Based on known password patterns.

**Example Patterns:**
```bash
# Word + 2 digits: password12
hashcat -m 0 -a 6 hash.txt wordlist.txt ?d?d

# Capital + 6 lowercase + 2 digits: Password12
hashcat -m 0 -a 3 hash.txt ?u?l?l?l?l?l?l?d?d

# Month + Year: January2024
# Use custom wordlist with months + mask for year
```

### Hybrid Attacks

Combine dictionary and brute force.

```bash
# Dictionary + mask
hashcat -m 0 -a 6 hash.txt wordlist.txt ?d?d?d

# Mask + dictionary
hashcat -m 0 -a 7 hash.txt ?d?d?d wordlist.txt
```

## NCL Tips

### Common Password Patterns

1. **Default passwords**
   - admin/admin
   - admin/password
   - root/toor
   - Check default-password.info

2. **Weak passwords**
   - password, password123
   - qwerty, 123456
   - admin, letmein

3. **Context-based**
   - Company name + year
   - Challenge theme + digits
   - Season + year

### Quick Wins

1. **Try online lookups first** (CrackStation)
2. **Use rockyou.txt** for dictionary attacks
3. **Check for common formats** (MD5 is fast to crack)
4. **Look for hints** in challenge description
5. **Try default credentials** for services

### Time Management

- **Fast hashes** (MD5, SHA-1, NTLM): Can brute force
- **Slow hashes** (bcrypt, scrypt): Need good wordlist
- **Password-protected files**: Usually weak passwords in CTF

### Tools Priority

1. Online lookup (instant)
2. Hashcat with rockyou (fast)
3. John with rules (medium)
4. Brute force (slow, last resort)

## Practice Resources

- HashKiller practice hashes
- CrackMes
- Root-Me password challenges
- PicoCTF forensics challenges

## Common Commands Summary

```bash
# Identify hash
hashid <hash>

# Hashcat MD5
hashcat -m 0 hash.txt rockyou.txt

# John the Ripper
john --wordlist=rockyou.txt hashes.txt

# ZIP cracking
zip2john file.zip > hash.txt && john hash.txt

# Online lookup
# Visit crackstation.net

# Show cracked
hashcat hash.txt --show
john --show hashes.txt
```

Remember: In CTF, passwords are usually crackable within reasonable time. If it's taking too long, reconsider your approach!

