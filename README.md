# Description

Currently there is no known way to visualize how the Arch mirrors are spread out and tiered to spot any bottlenecks. This is an effort to fix that. I uses publicly accessible data to process. 

You can run the code as is. It will cache the results to 2 files, one for IPs and one for Country lat/long combos. The final result is an html file with the markers. Currently only showing tier2 mirrors. 
# ToDo
- [ ] try to find location with either ipv4 or ipv6 dns record, continue with generic country instead
- [ ] add opt in to use something like ipinfo to make locations better 
- [ ] optimize tier1/2 finding...
- [ ] color randomization for markers with country finding
- [ ] connect tier 1/2 markers
- [ ] show tier 0 ?
- [ ] buttons to turn off tiers
- [ ] analyze how many downstream each t1/t0 mirror has, maybe show a legend
