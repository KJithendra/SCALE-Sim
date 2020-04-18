import math
import dram_trace as dram
import sram_traffic_os as sram
import sram_traffic_ws as sram_ws
import sram_traffic_is as sram_is

def gen_all_traces(
        array_h_first = 4,
        array_w_first = 4,
        array_h_second = 4,
        array_w_second = 4,
        single_array = 1,
        ifmap_h = 7, ifmap_w = 7,
        filt_h  = 3, filt_w = 3,
        num_channels = 3,
        strides = 1, num_filt = 8,

        data_flow = 'os',

        word_size_bytes = 1,
        filter_sram_size_first = 64, ifmap_sram_size_first= 64, ofmap_sram_size_first = 64,
        filter_sram_size_second = 64, ifmap_sram_size_second= 64, ofmap_sram_size_second = 64,

        filt_base = 1000000, ifmap_base=0, ofmap_base = 2000000,
        sram_read_trace_file_first = "sram0_read.csv",
        sram_read_trace_file_second = "sram1_read.csv",
        sram_write_trace_file_first = "sram0_write.csv",
        sram_write_trace_file_second = "sram1_write.csv",

        dram_filter_trace_file = "dram_filter_read.csv",
        dram_ifmap_trace_file = "dram_ifmap_read.csv",
        dram_ofmap_trace_file = "dram_ofmap_write.csv"
    ):

    sram_cycles = 0
    sram_cycles_first = 0
    sram_cycles_second = 0
    array_one_used = 0
    array_two_used = 0
    util        = 0

    dram_filter_trace_file_first = "dram_sram0_filter_read.csv"
    dram_ifmap_trace_file_first = "dram_sram0_ifmap_read.csv"
    dram_ofmap_trace_file_first = "dram_sram0_ofmap_write.csv"

    dram_filter_trace_file_second = "dram_sram1_filter_read.csv"
    dram_ifmap_trace_file_second = "dram_sram1_ifmap_read.csv"
    dram_ofmap_trace_file_second = "dram_sram1_ofmap_write.csv"

    print("Generating traces and bw numbers")
    if data_flow == 'os':

        num_filt_first = 0
        num_filt_second = 0

        i = 1

        no_of_filt_px = filt_h * filt_w * num_channels

        max_parallel_window_first = 1           #Since OS can't have more than one filter in a column given er vertical fold
        max_parallel_window_second = 1

        avail_filt_per_fold = (array_w_first*max_parallel_window_first) + (array_w_second*max_parallel_window_second)

        while True:
           filt_processing = i*avail_filt_per_fold

           if num_filt <= filt_processing:
              filt_pend = num_filt - ((i-1)*avail_filt_per_fold)

              if filt_pend <= (array_w_first*max_parallel_window_first) and filt_pend > (array_w_second*max_parallel_window_second): ##Accomodating the last fold in systolic 1
                 num_filt_first = num_filt_first + filt_pend

              elif filt_pend > (array_w_first*max_parallel_window_first) and filt_pend <= (array_w_second*max_parallel_window_second): ## Accomodating the last fold in systolic 2
                 num_filt_second = num_filt_second + filt_pend

              elif filt_pend == avail_filt_per_fold:
                 num_filt_first = num_filt_first + (array_w_first*max_parallel_window_first)
                 num_filt_second = num_filt_second + (array_w_second*max_parallel_window_second)

              elif filt_pend <= (array_w_first*max_parallel_window_first) and filt_pend <= (array_w_second*max_parallel_window_second):
                 col_ratio_first = float(filt_pend/(array_w_first*max_parallel_window_first))
                 col_ratio_second = float(filt_pend/(array_w_second*max_parallel_window_second))

                 if(col_ratio_first >= col_ratio_second):
                    num_filt_first = num_filt_first + filt_pend

                 else:
                    num_filt_second = num_filt_second + filt_pend

              else:
                 col_ratio_first = float((filt_pend-(array_w_second*max_parallel_window_second))/(array_w_first*max_parallel_window_first))
                 col_ratio_second = float((filt_pend-(array_w_first*max_parallel_window_first))/(array_w_second*max_parallel_window_second))

                 if(col_ratio_first > col_ratio_second):
                    num_filt_second = num_filt_second + (array_w_second*max_parallel_window_second)
                    num_filt_first = num_filt_first + (filt_pend-(array_w_second*max_parallel_window_second))

                 else:
                    num_filt_first = num_filt_first + (array_w_first*max_parallel_window_first)
                    num_filt_second = num_filt_second + (filt_pend-(array_w_first*max_parallel_window_first))

              col_idx_base = num_filt_first    ##Starting from systolic 1 and taking the systolic 1 filter count as the beginning for the next systolic as base addresss

              break

           else:

              num_filt_first = num_filt_first + (array_w_first*max_parallel_window_first)
              num_filt_second = num_filt_second + (array_w_second*max_parallel_window_second)

              i = i + 1

        if single_array == 1:
           num_filt_first = num_filt
           num_filt_second = 0

        if num_filt_first > 0:
           array_one_used = 1

           sram_cycles_first, util = \
               sram.sram_traffic(
                   dimension_rows= array_h_first,
                   dimension_cols= array_w_first,
                   ifmap_h=ifmap_h, ifmap_w=ifmap_w,
                   filt_h=filt_h, filt_w=filt_w,
                   num_channels=num_channels,
                   strides=strides, num_filt=num_filt_first, total_num_filt = num_filt,
                   filt_base=filt_base, ifmap_base=ifmap_base, col_idx_base = 0,
                   ofmap_base = ofmap_base,
                   sram_read_trace_file=sram_read_trace_file_first,
                   sram_write_trace_file=sram_write_trace_file_first
               )
        else:
           sram_cycles_first = 0

        if num_filt_second > 0:
           array_two_used = 1

           sram_cycles_second, util = \
               sram.sram_traffic(
                   dimension_rows= array_h_second,
                   dimension_cols= array_w_second,
                   ifmap_h=ifmap_h, ifmap_w=ifmap_w,
                   filt_h=filt_h, filt_w=filt_w,
                   num_channels=num_channels,
                   strides=strides, num_filt=num_filt_second, total_num_filt = num_filt,
                   filt_base=filt_base, ifmap_base=ifmap_base, col_idx_base = col_idx_base,
                   ofmap_base = ofmap_base,
                   sram_read_trace_file=sram_read_trace_file_second,
                   sram_write_trace_file=sram_write_trace_file_second
               )
        else:
           sram_cycles_second = 0

        sram_cycles = max(int(sram_cycles_first),int(sram_cycles_second))
    elif data_flow == 'ws':
       
        num_filt_first = 0
        num_filt_second = 0

        i = 1

        no_of_filt_px = filt_h * filt_w * num_channels

        if array_h_first < no_of_filt_px:
           max_parallel_window_first = 1
        else:
           max_parallel_window_first = math.floor(array_h_first/no_of_filt_px)

        if array_h_second < no_of_filt_px:
           max_parallel_window_second = 1
        else:
           max_parallel_window_second = math.floor(array_h_second/no_of_filt_px)

        avail_filt_per_fold = (array_w_first*max_parallel_window_first) + (array_w_second*max_parallel_window_second)

        while True:
           filt_processing = i*avail_filt_per_fold

           if num_filt <= filt_processing:
              filt_pend = num_filt - ((i-1)*avail_filt_per_fold)

              if filt_pend <= (array_w_first*max_parallel_window_first) and filt_pend > (array_w_second*max_parallel_window_second): ##Accomodating the last fold in systolic 1
                 num_filt_first = num_filt_first + filt_pend

              elif filt_pend > (array_w_first*max_parallel_window_first) and filt_pend <= (array_w_second*max_parallel_window_second): ## Accomodating the last fold in systolic 2
                 num_filt_second = num_filt_second + filt_pend

              elif filt_pend == avail_filt_per_fold:
                 num_filt_first = num_filt_first + (array_w_first*max_parallel_window_first)
                 num_filt_second = num_filt_second + (array_w_second*max_parallel_window_second)

              elif filt_pend <= (array_w_first*max_parallel_window_first) and filt_pend <= (array_w_second*max_parallel_window_second):
                 col_ratio_first = float(filt_pend/(array_w_first*max_parallel_window_first))
                 col_ratio_second = float(filt_pend/(array_w_second*max_parallel_window_second))

                 if(col_ratio_first >= col_ratio_second):
                    num_filt_first = num_filt_first + filt_pend

                 else:
                    num_filt_second = num_filt_second + filt_pend

              else:
                 col_ratio_first = float((filt_pend-(array_w_second*max_parallel_window_second))/(array_w_first*max_parallel_window_first))
                 col_ratio_second = float((filt_pend-(array_w_first*max_parallel_window_first))/(array_w_second*max_parallel_window_second))

                 if(col_ratio_first > col_ratio_second):
                    num_filt_second = num_filt_second + (array_w_second*max_parallel_window_second)
                    num_filt_first = num_filt_first + (filt_pend-(array_w_second*max_parallel_window_second))

                 else:
                    num_filt_first = num_filt_first + (array_w_first*max_parallel_window_first)
                    num_filt_second = num_filt_second + (filt_pend-(array_w_first*max_parallel_window_first))

              col_idx_base = num_filt_first    ##Starting from systolic 1 and taking the systolic 1 filter count as the beginning for the next systolic as base addresss

              break

           else:

              num_filt_first = num_filt_first + (array_w_first*max_parallel_window_first)
              num_filt_second = num_filt_second + (array_w_second*max_parallel_window_second)

              i = i + 1
 
        if single_array == 1:
           num_filt_first = num_filt
           num_filt_second = 0

        if num_filt_first > 0:
           array_one_used = 1
 
           sram_cycles_first, util = \
               sram_ws.sram_traffic(
                   dimension_rows = array_h_first,
                   dimension_cols = array_w_first,
                   ifmap_h = ifmap_h, ifmap_w = ifmap_w,
                   filt_h = filt_h, filt_w = filt_w,
                   num_channels = num_channels,
                   col_idx_base = 0, total_num_filt = num_filt,
                   strides = strides, num_filt = num_filt_first,
                   ofmap_base = ofmap_base, filt_base = filt_base, ifmap_base = ifmap_base,
                   sram_read_trace_file = sram_read_trace_file_first,
                   sram_write_trace_file = sram_write_trace_file_first
               )
        else:
           sram_cycles_first = 0

        if num_filt_second > 0:
           array_two_used = 1

           sram_cycles_second, util = \
              sram_ws.sram_traffic(
                  dimension_rows = array_h_second,
                  dimension_cols = array_w_second,
                  ifmap_h = ifmap_h, ifmap_w = ifmap_w,
                  filt_h = filt_h, filt_w = filt_w,
                  num_channels = num_channels,
                  col_idx_base = col_idx_base, total_num_filt = num_filt,
                  strides = strides, num_filt = num_filt_second,
                  ofmap_base = ofmap_base, filt_base = filt_base, ifmap_base = ifmap_base,
                  sram_read_trace_file = sram_read_trace_file_second,
                  sram_write_trace_file = sram_write_trace_file_second
              )
        else:
           sram_cycles_second = 0

        sram_cycles = max(int(sram_cycles_first),int(sram_cycles_second))
    elif data_flow == 'is':
        ofmap_h = (ifmap_h - filt_h)/strides + 1
        ofmap_w = (ifmap_w - filt_w)/strides + 1

        num_ofmap = ofmap_h * ofmap_w

        num_ofmap_first = 0
        num_ofmap_second = 0

        i = 1

        no_of_filt_px = filt_h * filt_w * num_channels

        if array_h_first < no_of_filt_px:
           max_parallel_window_first = 1
        else:
           max_parallel_window_first = math.floor(array_h_first/no_of_filt_px)

        if array_h_second < no_of_filt_px:
           max_parallel_window_second = 1
        else:
           max_parallel_window_second = math.floor(array_h_second/no_of_filt_px)

        avail_ofmap_per_fold = (array_w_first*max_parallel_window_first) + (array_w_second*max_parallel_window_second)

        while True:
           ofmap_processing = i*avail_ofmap_per_fold

           if num_ofmap <= ofmap_processing:
              ofmap_pend = num_ofmap - ((i-1)*avail_ofmap_per_fold)

              if ofmap_pend <= (array_w_first*max_parallel_window_first) and ofmap_pend > (array_w_second*max_parallel_window_second): ##Accomodating the last fold in systolic 1
                 num_ofmap_first = num_ofmap_first + ofmap_pend

              elif ofmap_pend > (array_w_first*max_parallel_window_first) and ofmap_pend <= (array_w_second*max_parallel_window_second): ## Accomodating the last fold in systolic 2
                 num_ofmap_second = num_ofmap_second + ofmap_pend

              elif ofmap_pend == avail_ofmap_per_fold:
                 num_ofmap_first = num_ofmap_first + (array_w_first*max_parallel_window_first)
                 num_ofmap_second = num_ofmap_second + (array_w_second*max_parallel_window_second)

              elif ofmap_pend <= (array_w_first*max_parallel_window_first) and ofmap_pend <= (array_w_second*max_parallel_window_second):
                 col_ratio_first = float(ofmap_pend/(array_w_first*max_parallel_window_first))
                 col_ratio_second = float(ofmap_pend/(array_w_second*max_parallel_window_second))

                 if(col_ratio_first >= col_ratio_second):
                    num_ofmap_first = num_ofmap_first + ofmap_pend

                 else:
                    num_ofmap_second = num_ofmap_second + ofmap_pend

              else:
                 col_ratio_first = float((ofmap_pend-(array_w_second*max_parallel_window_second))/(array_w_first*max_parallel_window_first))
                 col_ratio_second = float((ofmap_pend-(array_w_first*max_parallel_window_first))/(array_w_second*max_parallel_window_second))

                 if(col_ratio_first > col_ratio_second):
                    num_ofmap_second = num_ofmap_second + (array_w_second*max_parallel_window_second)
                    num_ofmap_first = num_ofmap_first + (ofmap_pend-(array_w_second*max_parallel_window_second))

                 else:
                    num_ofmap_first = num_ofmap_first + (array_w_first*max_parallel_window_first)
                    num_ofmap_second = num_ofmap_second + (ofmap_pend-(array_w_first*max_parallel_window_first))

              col_idx_base = num_ofmap_first    ##Starting from systolic 1 and taking the systolic 1 filter count as the beginning for the next systolic as base addresss

              break

           else:

              num_ofmap_first = num_ofmap_first + (array_w_first*max_parallel_window_first)
              num_ofmap_second = num_ofmap_second + (array_w_second*max_parallel_window_second)

              i = i + 1

        if single_array == 1:
           num_ofmap_first = num_ofmap
           num_ofmap_second = 0

        if num_ofmap_first > 0:
           array_one_used = 1

           sram_cycles_first, util = \
               sram_is.sram_traffic(
                   dimension_rows = array_h_first,
                   dimension_cols = array_w_first,
                   ifmap_h = ifmap_h, ifmap_w = ifmap_w,
                   filt_h = filt_h, filt_w = filt_w,
                   num_channels = num_channels, num_ofmap = num_ofmap_first,
                   strides = strides, num_filt = num_filt,
                   col_idx_base = 0,
                   ofmap_base = ofmap_base, filt_base = filt_base, ifmap_base = ifmap_base,
                   sram_read_trace_file = sram_read_trace_file_first,
                   sram_write_trace_file = sram_write_trace_file_first
               )
        else:
           sram_cycles_first = 0

        if num_ofmap_second > 0:
           array_two_used = 1

           sram_cycles_second, util = \
               sram_is.sram_traffic(
                   dimension_rows = array_h_second,
                   dimension_cols = array_w_second,
                   ifmap_h = ifmap_h, ifmap_w = ifmap_w,
                   filt_h = filt_h, filt_w = filt_w,
                   num_channels = num_channels, num_ofmap = num_ofmap_second,
                   strides = strides, num_filt = num_filt,
                   col_idx_base = col_idx_base,
                   ofmap_base = ofmap_base, filt_base = filt_base, ifmap_base = ifmap_base,
                   sram_read_trace_file = sram_read_trace_file_second,
                   sram_write_trace_file = sram_write_trace_file_second
               )
        else:
           sram_cycles_second = 0

        sram_cycles = max(int(sram_cycles_first),int(sram_cycles_second))

    #print("Generating DRAM traffic")
    if array_one_used == 1:
       if single_array == 1 or array_two_used == 0:
          dram.dram_trace_read_v2(
              sram_sz=ifmap_sram_size_first,
              word_sz_bytes=word_size_bytes,
              min_addr=ifmap_base, max_addr=filt_base,
              sram_trace_file=sram_read_trace_file_first,
              dram_trace_file=dram_ifmap_trace_file
          )

          dram.dram_trace_read_v2(
              sram_sz= filter_sram_size_first,
              word_sz_bytes= word_size_bytes,
              min_addr=filt_base, max_addr=ofmap_base,
              sram_trace_file= sram_read_trace_file_first,
              dram_trace_file= dram_filter_trace_file
          )

          dram.dram_trace_write(
              ofmap_sram_size= ofmap_sram_size_first,
              data_width_bytes= word_size_bytes,
              sram_write_trace_file= sram_write_trace_file_first,
              dram_write_trace_file= dram_ofmap_trace_file
          )
       else:
          dram.dram_trace_read_v2(
              sram_sz=ifmap_sram_size_first,
              word_sz_bytes=word_size_bytes,
              min_addr=ifmap_base, max_addr=filt_base,
              sram_trace_file=sram_read_trace_file_first,
              dram_trace_file=dram_ifmap_trace_file_first
          )

          dram.dram_trace_read_v2(
              sram_sz= filter_sram_size_first,
              word_sz_bytes= word_size_bytes,
              min_addr=filt_base, max_addr=ofmap_base,
              sram_trace_file= sram_read_trace_file_first,
              dram_trace_file= dram_filter_trace_file_first
          )

          dram.dram_trace_write(
              ofmap_sram_size= ofmap_sram_size_first,
              data_width_bytes= word_size_bytes,
              sram_write_trace_file= sram_write_trace_file_first,
              dram_write_trace_file= dram_ofmap_trace_file_first
          )

    if array_two_used == 1:
       if array_one_used == 0:
          dram.dram_trace_read_v2(
              sram_sz=ifmap_sram_size_second,
              word_sz_bytes=word_size_bytes,
              min_addr=ifmap_base, max_addr=filt_base,
              sram_trace_file=sram_read_trace_file_second,
              dram_trace_file=dram_ifmap_trace_file
          )

          dram.dram_trace_read_v2(
              sram_sz= filter_sram_size_second,
              word_sz_bytes= word_size_bytes,
              min_addr=filt_base, max_addr=ofmap_base,
              sram_trace_file= sram_read_trace_file_second,
              dram_trace_file= dram_filter_trace_file
          )

          dram.dram_trace_write(
              ofmap_sram_size= ofmap_sram_size_second,
              data_width_bytes= word_size_bytes,
              sram_write_trace_file= sram_write_trace_file_second,
              dram_write_trace_file= dram_ofmap_trace_file
          )
       else:   
          dram.dram_trace_read_v2(
              sram_sz=ifmap_sram_size_second,
              word_sz_bytes=word_size_bytes,
              min_addr=ifmap_base, max_addr=filt_base,
              sram_trace_file=sram_read_trace_file_second,
              dram_trace_file=dram_ifmap_trace_file_second
          )

          dram.dram_trace_read_v2(
              sram_sz= filter_sram_size_second,
              word_sz_bytes= word_size_bytes,
              min_addr=filt_base, max_addr=ofmap_base,
              sram_trace_file= sram_read_trace_file_second,
              dram_trace_file= dram_filter_trace_file_second
          )

          dram.dram_trace_write(
              ofmap_sram_size= ofmap_sram_size_second,
              data_width_bytes= word_size_bytes,
              sram_write_trace_file= sram_write_trace_file_second,
              dram_write_trace_file= dram_ofmap_trace_file_second
          )


    # Selvaraj: Merge both DRAM traffic CSV's for BW calculations
    if array_one_used == 1 and array_two_used == 1:
       sram_controller(dram_ifmap_trace_file_first,dram_ifmap_trace_file_second,dram_ifmap_trace_file)
       sram_controller(dram_filter_trace_file_first,dram_filter_trace_file_second,dram_filter_trace_file)
       sram_controller(dram_ofmap_trace_file_first,dram_ofmap_trace_file_second,dram_ofmap_trace_file)


    print("Average utilization : \t"  + str(util) + " %")
    print("Cycles for compute  : \t"  + str(sram_cycles) + " cycles")


    if single_array == 1:   # SCALE-Sim used as a single compute array simulator
       bw_numbers, detailed_log  = gen_bw_numbers(both_array_used = 0,array_one_idle = 0,array_two_idle = 0,dram_ifmap_trace_file = dram_ifmap_trace_file,dram_filter_trace_file =  dram_filter_trace_file, #Selvaraj: Add support for two SRAM based BW generation after DRAM merge
                                    dram_ofmap_trace_file = dram_ofmap_trace_file,sram_write_trace_file_first =  sram_write_trace_file_first,
                                    sram_read_trace_file_first = sram_read_trace_file_first) 
                                    #array_h, array_w)


    elif (array_one_used == 1 and array_two_used == 0):   ## Second array not powered on at all
       bw_numbers, detailed_log  = gen_bw_numbers(both_array_used = 1, array_one_idle = 0,array_two_idle = 1,dram_ifmap_trace_file = dram_ifmap_trace_file,dram_filter_trace_file =  dram_filter_trace_file,
                                    dram_ofmap_trace_file = dram_ofmap_trace_file,sram_write_trace_file_first =  sram_write_trace_file_first,
                                    sram_read_trace_file_first = sram_read_trace_file_first)


    elif (array_one_used == 0 and array_two_used == 1):   ## First array not powered on at all
       bw_numbers, detailed_log  = gen_bw_numbers(both_array_used = 1,array_one_idle = 1,array_two_idle = 0,dram_ifmap_trace_file = dram_ifmap_trace_file,dram_filter_trace_file =  dram_filter_trace_file,
                                    dram_ofmap_trace_file = dram_ofmap_trace_file,sram_write_trace_file_first =  sram_write_trace_file_second,
                                    sram_read_trace_file_first = sram_read_trace_file_second)


    elif array_one_used == 1 and array_two_used == 1:
       bw_numbers, detailed_log  = gen_bw_numbers(both_array_used = 1, array_one_idle = 0, array_two_idle = 0, dram_ifmap_trace_file = dram_ifmap_trace_file,dram_filter_trace_file = dram_filter_trace_file,
                                    dram_ofmap_trace_file=dram_ofmap_trace_file, sram_write_trace_file_first=sram_write_trace_file_first,
                                    sram_read_trace_file_first = sram_read_trace_file_first, sram_write_trace_file_second = sram_write_trace_file_second,
                                    sram_read_trace_file_second = sram_read_trace_file_second)
                                    #array_h, array_w)


    return bw_numbers, detailed_log, util, str(sram_cycles), array_one_used, array_two_used


def gen_max_bw_numbers(both_array_used, array_one_idle, array_two_idle, dram_ifmap_trace_file, dram_filter_trace_file,
                    dram_ofmap_trace_file, sram_write_trace_file_first, sram_read_trace_file_first, sram_write_trace_file_second = "sram1_write.csv", sram_read_trace_file_second = "sram1_read.csv"
                    ):

    max_dram_activation_bw = 0
    num_bytes = 0
    max_dram_act_clk = ""
    f = open(dram_ifmap_trace_file, 'r')

    for row in f:
        clk = row.split(',')[0]
        num_bytes = len(row.split(',')) - 2
        
        
        if max_dram_activation_bw < num_bytes:
            max_dram_activation_bw = num_bytes
            max_dram_act_clk = clk
    f.close()

    max_dram_filter_bw = 0
    num_bytes = 0
    max_dram_filt_clk = ""
    f = open(dram_filter_trace_file, 'r')

    for row in f:
        clk = row.split(',')[0]
        num_bytes = len(row.split(',')) - 2

        if max_dram_filter_bw < num_bytes:
            max_dram_filter_bw = num_bytes
            max_dram_filt_clk = clk

    f.close()

    max_dram_ofmap_bw = 0
    num_bytes = 0
    max_dram_ofmap_clk = ""
    f = open(dram_ofmap_trace_file, 'r')

    for row in f:
        clk = row.split(',')[0]
        num_bytes = len(row.split(',')) - 2

        if max_dram_ofmap_bw < num_bytes:
            max_dram_ofmap_bw = num_bytes
            max_dram_ofmap_clk = clk

    f.close()

    if (both_array_used == 1 and array_one_idle == 0) or both_array_used == 0:    
       max_sram0_ofmap_bw = 0
       num_bytes = 0
       f = open(sram_write_trace_file_first, 'r')

       for row in f:
           num_bytes = len(row.split(',')) - 2

           if max_sram0_ofmap_bw < num_bytes:
            max_sram0_ofmap_bw = num_bytes

       f.close()

       max_sram0_read_bw = 0
       num_bytes = 0
       f = open(sram_read_trace_file_first, 'r')

       for row in f:
           num_bytes = len(row.split(',')) - 2

           if max_sram0_read_bw < num_bytes:
               max_sram0_read_bw = num_bytes

       f.close()
       

    if both_array_used == 1 and array_two_idle == 0:
       max_sram1_ofmap_bw = 0
       num_bytes = 0
       f = open(sram_write_trace_file_second, 'r')

       for row in f:
           num_bytes = len(row.split(',')) - 2

           if max_sram1_ofmap_bw < num_bytes:
               max_sram1_ofmap_bw = num_bytes

       f.close()

       max_sram1_read_bw = 0
       num_bytes = 0
       f = open(sram_read_trace_file_second, 'r')

       for row in f:
           num_bytes = len(row.split(',')) - 2

           if max_sram1_read_bw < num_bytes:
               max_sram1_read_bw = num_bytes

       f.close()

    #print("DRAM IFMAP Read BW, DRAM Filter Read BW, DRAM OFMAP Write BW, SRAM OFMAP Write BW")
    log  = str(max_dram_activation_bw) + ",\t" + str(max_dram_filter_bw) + ",\t" 
    log += str(max_dram_ofmap_bw)

    if (both_array_used == 1 and array_one_idle == 0) or both_array_used == 0:
       log += ",\t" + str(max_sram0_read_bw) + ",\t" + str(max_sram0_ofmap_bw)  + ","
    elif array_one_idle == 1:
       log += "\tN/A ,\tN/A ,"

    if (both_array_used == 1 and array_two_idle == 0):
       log += "\t" + str (max_sram1_read_bw) + ",\t" + str(max_sram1_ofmap_bw) + ","
    elif array_two_idle == 1:
       log += "\tN/A ,\tN/A ,"
    # Anand: Enable the following for debug print
    #log += str(max_dram_act_clk) + ",\t" + str(max_dram_filt_clk) + ",\t"
    #log += str(max_dram_ofmap_clk) + ","
    #print(log)
    return log


def gen_bw_numbers( both_array_used, array_one_idle, array_two_idle,
                    dram_ifmap_trace_file, dram_filter_trace_file,
                    dram_ofmap_trace_file, sram_write_trace_file_first, 
                    sram_read_trace_file_first, sram_write_trace_file_second = "sram1_write.csv",
                    sram_read_trace_file_second = "sram1_read.csv"
                    #sram_read_trace_file,
                    #array_h, array_w        # These are needed for utilization calculation
                    ):

    min_clk = 100000
    max_clk = -1
    detailed_log = ""

    num_dram_activation_bytes = 0
    f = open(dram_ifmap_trace_file, 'r')
    start_clk = 0
    first = True

    for row in f:
        num_dram_activation_bytes += len(row.split(',')) - 2
        
        elems = row.strip().split(',')
        clk = float(elems[0])

        if first:
            first = False
            start_clk = clk

        if clk < min_clk:
            min_clk = clk

    stop_clk = clk
    detailed_log += str(start_clk) + ",\t" + str(stop_clk) + ",\t" + str(num_dram_activation_bytes) + ",\t"
    f.close()

    num_dram_filter_bytes = 0
    f = open(dram_filter_trace_file, 'r')
    first = True

    for row in f:
        num_dram_filter_bytes += len(row.split(',')) - 2

        elems = row.strip().split(',')
        clk = float(elems[0])

        if first:
            first = False
            start_clk = clk

        if clk < min_clk:
            min_clk = clk

    stop_clk = clk
    detailed_log += str(start_clk) + ",\t" + str(stop_clk) + ",\t" + str(num_dram_filter_bytes) + ",\t"
    f.close()

    num_dram_ofmap_bytes = 0
    f = open(dram_ofmap_trace_file, 'r')
    first = True

    for row in f:
        num_dram_ofmap_bytes += len(row.split(',')) - 2

        elems = row.strip().split(',')
        clk = float(elems[0])

        if first:
            first = False
            start_clk = clk

    stop_clk = clk
    detailed_log += str(start_clk) + ",\t" + str(stop_clk) + ",\t" + str(num_dram_ofmap_bytes) + ",\t"
    f.close()
    if clk > max_clk:
        max_clk = clk

    if (both_array_used == 1 and array_one_idle == 0) or both_array_used == 0:
       num_sram0_ofmap_bytes = 0
       f = open(sram_write_trace_file_first, 'r')
       first = True

       for row in f:
           num_sram0_ofmap_bytes += len(row.split(',')) - 2
           elems = row.strip().split(',')
           clk = float(elems[0])

           if first:
               first = False
               start_clk = clk

       stop_clk = clk
       detailed_log += str(start_clk) + ",\t" + str(stop_clk) + ",\t" + str(num_sram0_ofmap_bytes) + ",\t"
       f.close()
       if clk > max_clk:
           max_clk = clk
    elif array_one_idle == 1:
       detailed_log += "N/A ,\t" + "N/A ,\t" + "N/A ,\t"

    if both_array_used == 1 and array_two_idle == 0:
       num_sram1_ofmap_bytes = 0
       f = open(sram_write_trace_file_second, 'r')
       first = True

       for row in f:
           num_sram1_ofmap_bytes += len(row.split(',')) - 2
           elems = row.strip().split(',')
           clk = float(elems[0])

           if first:
               first = False
               start_clk = clk

       stop_clk = clk
       detailed_log += str(start_clk) + ",\t" + str(stop_clk) + ",\t" + str(num_sram1_ofmap_bytes) + ",\t"
       f.close()
       if clk > max_clk:
           max_clk = clk
    elif array_two_idle == 1:
       detailed_log += "N/A ,\t" + "N/A ,\t" + "N/A ,\t"

    if (both_array_used == 1 and array_one_idle == 0) or both_array_used == 0:    
       num_sram0_read_bytes = 0
       total_util = 0
       #print("Opening " + sram_trace_file)
       f = open(sram_read_trace_file_first, 'r')
       first = True

       for row in f:
           #num_sram0_read_bytes += len(row.split(',')) - 2
           elems = row.strip().split(',')
           clk = float(elems[0])

           if first:
               first = False
               start_clk = clk

           #util, valid_bytes = parse_sram_read_data(elems[1:-1], array_h, array_w)
           valid_bytes = parse_sram_read_data(elems[1:])
           num_sram0_read_bytes += valid_bytes
           #total_util += util
           #print("Total Util " + str(total_util) + ", util " + str(util))

       stop_clk = clk
       detailed_log += str(start_clk) + ",\t" + str(stop_clk) + ",\t" + str(num_sram0_read_bytes) + ",\t"
       f.close()
       sram_clk = clk
       if clk > max_clk:
           max_clk = clk
    elif array_one_idle == 1:
       detailed_log += "N/A ,\t" + "N/A ,\t" + "N/A ,\t"

    if both_array_used == 1:
       num_sram1_read_bytes = 0
       total_util = 0
       #print("Opening " + sram_trace_file)
       f = open(sram_read_trace_file_second, 'r')
       first = True

       for row in f:
           #num_sram1_read_bytes += len(row.split(',')) - 2
           elems = row.strip().split(',')
           clk = float(elems[0])

           if first:
               first = False
               start_clk = clk

           #util, valid_bytes = parse_sram_read_data(elems[1:-1], array_h, array_w)
           valid_bytes = parse_sram_read_data(elems[1:])
           num_sram1_read_bytes += valid_bytes
           #total_util += util
           #print("Total Util " + str(total_util) + ", util " + str(util))

       stop_clk = clk
       detailed_log += str(start_clk) + ",\t" + str(stop_clk) + ",\t" + str(num_sram1_read_bytes) + ",\t"
       f.close()
       sram_clk = clk
       if clk > max_clk:
           max_clk = clk
    elif array_two_idle == 1:
       detailed_log += "N/A ,\t" + "N/A ,\t" + "N/A ,\t" 

    delta_clk = max_clk - min_clk

    dram_activation_bw  = num_dram_activation_bytes / delta_clk
    dram_filter_bw      = num_dram_filter_bytes / delta_clk
    dram_ofmap_bw       = num_dram_ofmap_bytes / delta_clk
    sram0_ofmap_bw       = num_sram0_ofmap_bytes / delta_clk
    sram0_read_bw        = num_sram0_read_bytes / delta_clk

    if both_array_used == 1:
       sram1_ofmap_bw       = num_sram1_ofmap_bytes / delta_clk
       sram1_read_bw        = num_sram1_read_bytes / delta_clk
    #print("total_util: " + str(total_util) + ", sram_clk: " + str(sram_clk))
    #avg_util            = total_util / sram_clk * 100

    units = " Bytes/cycle"
    print("DRAM IFMAP Read BW  : \t" + str(dram_activation_bw) + units)
    print("DRAM Filter Read BW : \t" + str(dram_filter_bw) + units)
    print("DRAM OFMAP Write BW : \t" + str(dram_ofmap_bw) + units)
    #print("Average utilization : \t"  + str(avg_util) + " %")
    #print("SRAM OFMAP Write BW, Min clk, Max clk")
    
    log = str(dram_activation_bw) + ",\t" + str(dram_filter_bw) + ",\t" + str(dram_ofmap_bw)

    if (both_array_used == 1 and array_one_idle == 0) or both_array_used == 0:
       log +=  ",\t" + str(sram0_read_bw) + ",\t" + str(sram0_ofmap_bw) + ","

    elif array_one_idle == 1:
       log += "\tN/A ,\tNA ,"

    if both_array_used == 1 and array_two_idle == 0:
       log += "\t" + str(sram1_read_bw) + ",\t" + str(sram1_ofmap_bw) + ","
    elif array_two_idle == 1:
       log += "\tN/A ,\tNA ,"
    # Anand: Enable the following line for debug
    #log += str(min_clk) + ",\t" + str(max_clk) + ","
    #print(log)
    #return log, avg_util
    return log, detailed_log

def prune(input_list):
    l = []

    for e in input_list:
        e = e.strip()
        if e != '' and e != ' ':
            l.append(e)

    return l

def sram_controller (
   sram0_trace_file = "sram0.csv",
   sram1_trace_file = "sram1.csv",
   dram_trace_file = "dram_trace.csv"
   ):

   sram0_requests = open(sram0_trace_file,"r")
   sram1_requests = open(sram1_trace_file,"r")

   dram = open(dram_trace_file,"w")

   sram0_done = False
   sram1_done = False

   accept_sram0_req = 1
   accept_sram1_req = 1

   while sram0_done == False or sram1_done == False:

     if accept_sram0_req == 1 and sram0_done == False:
        sram0_request = sram0_requests.readline()

     if accept_sram1_req == 1 and sram1_done == False:
        sram1_request = sram1_requests.readline()

     if not sram0_request:
        sram0_done = True
     else:
        sram0_addr = sram0_request.strip().split(',')
        sram0_addr = prune(sram0_addr)
        sram0_addr = [float(x) for x in sram0_addr]

     if not sram1_request:
        sram1_done = True
     else:
        sram1_addr = sram1_request.strip().split(',')
        sram1_addr = prune(sram1_addr)
        sram1_addr = [float(x) for x in sram1_addr]

     sram0_clk = sram0_addr[0]
     sram1_clk = sram1_addr[0]

     if sram0_done == True and sram1_done == True: #Waive this iteration
        break

     elif sram0_done == True:                 #I'm done with SRAM0, you can continue with SRAM 1 wihtout any race
        trace = ""
        for entry in sram1_addr:
           trace += str(entry) + ", "

        trace += "\n"
        dram.write(trace)

        accept_sram1_req = 1
        accept_sram0_req = 1

     elif sram1_done == True:                #I'm done with SRAM1, you can continue with SRAM 0 wihtout any race
        trace = ""
        for entry in sram0_addr:
           trace += str(entry) + ", "

        trace += "\n"
        dram.write(trace)

        accept_sram0_req = 1
        accept_sram1_req = 0
    
     elif sram0_clk < sram1_clk:   #Accelerate SRAM0 and wait SRAM1 till both are in sync
        trace = ""
        for entry in sram0_addr:
           trace += str(entry) + ", "

        trace += "\n"
        dram.write(trace)

        accept_sram0_req = 1
        accept_sram1_req = 0

     elif sram0_clk == sram1_clk:    ##Common address makes only one read if it happens during the same cycle

        trace = ""
        duplicate_value = 0

        for entry in sram0_addr:
           trace += str(entry) + ", "

        for j in sram1_addr:
           for i in sram0_addr:
              if i==j:
                 duplicate_value = 1

           if duplicate_value == 0:
              trace += str(j) + ", "

           duplicate_value = 0

        trace += "\n"
        dram.write(trace)

        accept_sram0_req = 1
        accept_sram1_req = 1

     else:                           #Accelerate SRAM1 and wait SRAM0 till both are in sync
        trace = ""
        for entry in sram1_addr:
           trace += str(entry) + ", "

        trace += "\n"
        dram.write(trace)

        accept_sram0_req = 0
        accept_sram1_req = 1

   sram0_requests.close()
   sram1_requests.close()

   dram.close()

#def parse_sram_read_data(elems, array_h, array_w):
def parse_sram_read_data(elems):
    #half = int(len(elems) /2)
    #nz_row = 0
    #nz_col = 0
    data = 0

    for i in range(len(elems)):
        e = elems[i]
        if e != ' ':
            data += 1
            #if i < half:
            #if i < array_h:
            #    nz_row += 1
            #else:
            #    nz_col += 1

    #util = (nz_row * nz_col) / (half * half)
    #util = (nz_row * nz_col) / (array_h * array_w)
    #data = nz_row + nz_col
    
    #return util, data
    return data


def test():
    test_fc1_24x24 = [27, 37, 512, 27, 37, 512, 1, 24, 1]
    test_yolo_tiny_conv1_24x24 = [418, 418, 3, 3, 3, 16, 1, 24, 1]
    test_mdnet_conv1_24x24 = [107, 107, 3, 7, 7, 96, 2, 24, 1]

    #param = test_fc1_24x24
    #param = test_yolo_tiny_conv1_24x24
    param = test_mdnet_conv1_24x24

    # The parameters for 1st layer of yolo_tiny
    ifmap_h = param[0]
    ifmap_w = param[1]
    num_channels = param[2]

    filt_h = param[3]
    filt_w = param[4]
    num_filters = param[5] #16

    strides = param[6]

    # Model parameters
    dimensions = param[7] #32 #16
    word_sz = param[8]

    filter_sram_size = 1 * 1024
    ifmap_sram_size = 1 * 1024
    ofmap_sram_size = 1 * 1024

    filter_base = 1000000
    ifmap_base = 0
    ofmap_base = 2000000

    # Trace files
    sram_read_trace = "test_sram_read.csv"
    sram_write_trace  = "test_sram_write.csv"

    dram_filter_read_trace = "test_dram_filt_read.csv"
    dram_ifmap_read_trace  = "test_dram_ifamp_read.csv"
    dram_write_trace = "test_dram_write.csv"

    gen_all_traces(
        array_h = dimensions,
        array_w = dimensions,
        ifmap_h= ifmap_h, ifmap_w= ifmap_w, num_channels=num_channels,
        filt_h= filt_h, filt_w= filt_w, num_filt= num_filters,
        strides= strides,

        filter_sram_size= filter_sram_size, ifmap_sram_size= ifmap_sram_size, ofmap_sram_size= ofmap_sram_size,
        word_size_bytes= word_sz, filt_base= filter_base, ifmap_base= ifmap_base,

        sram_read_trace_file= sram_read_trace, sram_write_trace_file= sram_write_trace,

        dram_filter_trace_file= dram_filter_read_trace,
        dram_ifmap_trace_file= dram_ifmap_read_trace,
        dram_ofmap_trace_file= dram_write_trace
    )


if __name__ == "__main__":
    test()
