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
We also need to download the boundary days: 2023-365 and 2025-001 so that 30h tropNom files could be generated for 2024-001 and 2024-365.

```bash
rclone sync vmf:GRID/2.5x2/VMF1/STD_OP/ products/VMF1/ --include="2023/{ah,aw,zh,zw}23365*" --transfers 16 --checkers 32 -v
```

```bash
rclone sync vmf:GRID/2.5x2/VMF1/STD_OP/ products/VMF1/ --include="2025/{ah,aw,zh,zw}25001*" --transfers 16 --checkers 32 -v
```

The files have to be gzipped: `gzip -r products/VMF1` and moved into the respective dirs: ah, aw etc within year dir:

```bash
for prefix in ah aw zh zw; do mkdir -p "$prefix" && mv ${prefix}* "$prefix/"; done
```

or from level above, where year dirs are present:

```bash
find . -maxdepth 1 -type d -regex './[0-9]+' -exec bash -c 'cd "$0" && for p in ah aw zh zw; do mkdir -p "$p" && mv "${p}"* "$p/"; done' {} \;
```

Get the orography_ell from http://vmf.geo.tuwien.ac.at/station_coord_files/orography_ell and save it into the root of VMF1

With the final directory structure as follows:
```
VMF1/
├── 2023
│   ├── ah
│   │   └── ah23365.*.gz
│   ├── aw
│   │   └── aw23365.*.gz
│   ├── zh
│   │   └── zh23365.*.gz
│   └── zw
│       └── zw23365.*.gz
├── 2024
│   ├── ah
│   │   └── ah24*.*.gz
│   ├── aw
│   │   └── aw24*.*.gz
│   ├── zh
│   │   └── zh24*.*.gz
│   └── zw
│       └── zw24*.*.gz
├── 2025
│   ├── ah
│   │   └── ah25001.*.gz
│   ├── aw
│   │   └── aw25001.*.gz
│   ├── zh
│   │   └── zh25001.*.gz
│   └── zw
│       └── zw25001.*.gz
└── orography_ell.gz
```
[!WARN] Outdated GipsyX (e.g. 1.3) can not run with IGS20 orbit and clock products (`JPL_GNSS_Products`) and will fail with:
```
E::1000035::rtgx started with command::rtgx Trees/ppp_0.tree
A::1000003::Invalid Input fatal error on start-up initialization::Invalid Input fatal error on start-up initialization::Error reading GEOP file "GNSSinitValues/GNSS.eo" Error in geopReader(): "IERS2020" is an unrecognized Extended_EO_Model.:::: FATAL ERROR!
```
The particular version of GipsyX will thus only work with IGS14 products. Example below.


### IGS14 PPP Processing with GipsyX
[!NOTE] Legacy files are provided in the form of tarballs and so to process data from 2014, tarballs from 2013 and 2015 should also be downloaded:

```
bash
rclone sync vmf:GRID/2.5x2/VMF1/STD_OP/ products/VMF1/ --include="201[3-5]/{ah,aw,zh,zw}*" --transfers 16 --checkers 32 -v
```

Untar (from the inside of VMF1 dir) with e.g.: 
```
find ???? -maxdepth 1 -type f -name '*.tar' -exec sh -c 'for f; do tar -xf "$f" -C "$(dirname "$f")"; done' _ {} +
```
gzip and move to the respective dirs as above.

The rest of 2014 products can be downloaded with:
```bash
rclone sync ga:rinex/daily/ data/ --include "2014/*/{hob2,alic,str2}*d.gz" -v --transfers 16 --checkers 32 --checksum
```

```bash
rclone sync jpl: products/ --include="JPL_GNSS_Products_IGS14/Final/2014/*" -v --transfers 16 --checkers 32 --checksum
```


```bash
rclone sync jpl:iono_daily/ products/ --include="IONEX_final/y2014/JPLG*gz" -v --transfers 16 --checkers 32 --checksum
```


