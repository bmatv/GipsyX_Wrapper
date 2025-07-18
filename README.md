# GipsyX_Wrapper
A python wrapper around JPL's GipsyX for efficient processing of multi station and multi year datasets. Supports GPS-only, GLONASS-only and GPS+GLONASS PPP modes. The wrapper can use arbitrary number of threads to convert RINEX to datarecord format, process and gather the data. GipsyX solution files are extracted into pandas DataFrames and saved as a serialized ZSTD container files. Finally, the solutions are analysed with Eterna software.

It has all the necessary modules needed for products and data preparation such as: IONEX files merging, tropnominals generation, orbit and clock products conversion and merging etc. All multithreaded.

Additionally, a pbs-script based submission method is added to efficiently utilize PBS clusters.

# A small tutorial

## Getting the data

We will be using rclone to get the data and products. Here's a sample config:
```
[ga]
type = sftp
host = sftp.data.gnss.ga.gov.au
user = anonymous
pass = your_email
shell_type = unix
md5sum_command = none
sha1sum_command = none

[jpl]
type = http
url = https://sideshow.jpl.nasa.gov/pub/
no_head = true

[vmf]
type = http
url = https://vmf.geo.tuwien.ac.at/trop_products/
no_head = true
```

## RINEX data
```bash
rclone sync ga:rinex/daily/ data/ --include "2024/*/{HOB2,ALIC,STR2}*crx.gz" -v --transfers 16 --checkers 32 --checksum
```


## IGS site logs
```bash
rclone sync ga: . --include "site-logs/text/*" -v --transfers 16 --checkers 32 --checksum
```

## GNSS Products
```bash
rclone sync jpl: products/ --include="JPL_GNSS_Products/Final/2024/*" -v --transfers 16 --checkers 32 --checksum
```

## Ionosphere Products
```bash
rclone sync jpl:iono_daily/ products/ --include="IONEX_final/y2024/JPLG*gz" -v --transfers 16 --checkers 32 --checksum
```

## Troposphere Products

>[!NOTE]
This is likely outdated but valid for GipsyX v1.3

```bash
rclone sync vmf:GRID/2.5x2/VMF1/STD_OP/ products/VMF1/ --include="2024/{ah,aw,zh,zw}*" --transfers 16 --checkers 32 -v
```

The files have to be gzipped: `gzip -r products/VMF1` and moved into the respective dirs: ah, aw etc within year dir:

```bash
for prefix in ah aw zh zw; do mkdir -p "$prefix" && mv ${prefix}* "$prefix/"; done
```

or from level above, where year dirs are present:

```bash
find . -maxdepth 1 -type d -regex './[0-9]\{4\}' -exec bash -c 'cd "$0" && for p in ah aw zh zw; do mkdir -p "$p" && mv "${p}"* "$p/" 2>/dev/null; done' {} \;
```

With the final directory structure as follows:

```
VMF1/
└── 2024
    ├── ah
    │   ├── ah24001.h00.gz
    │   ├── ah24001.h06.gz
    │   ├── ...
    ├── aw
    │   ├── ah24001.h00.gz
    │   ├── ah24001.h06.gz
    │   ├── ...
    ├── zh
    │   ├── ah24001.h00.gz
    │   ├── ah24001.h06.gz
    │   ├── ...
    └── zw
        ├── ah24001.h00.gz
        ├── ah24001.h06.gz
        ├── ...
        └── zw24366.h18.gz
```


