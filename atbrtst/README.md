![atbr](https://s3.amazonaws.com/atbr/atbr_small.png)

### What is atbrtst?

Low-latency prefix search for harddrives and SSDs


### Why atbrtst?

    1) Nice for large-scale search of relatively static data

### Building index on (ssd) disk

    cd atbr/atbrtst/builder
    python build_tree_on_disk.py <inputfilename> >diskindex 2>err 
    
### Use index from (c++) client

    cd atbr/atbrtst/client
    make
    ./atbr_lookup ../builder/diskindex <term_or_prefix_to_lookup>

### Where is the documentation?

http://atbr.atbrox.com/



    






    
    

     

    



