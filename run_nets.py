import trace_gen_wrapper as tg
import os
import subprocess


def run_net( ifmap_sram_size_first=1,
             filter_sram_size_first=1,
             ofmap_sram_size_first=1,
             ifmap_sram_size_second=1,
             filter_sram_size_second=1,
             ofmap_sram_size_second=1,
             array_h_first=32,
             array_w_first=32,
             array_h_second = 32,
             array_w_second = 31,
             single_array = 1,
             data_flow = 'os',
             topology_file = './topologies/yolo_v2.csv',
             net_name='yolo_v2',
             offset_list = [0, 10000000, 20000000]
            ):

    ifmap_sram_size_first *= 1024
    filter_sram_size_first *= 1024
    ofmap_sram_size_first *= 1024

    ifmap_sram_size_second *= 1024
    filter_sram_size_second *= 1024
    ofmap_sram_size_second *= 1024

    #fname = net_name + ".csv"
    param_file = open(topology_file, 'r')

    fname = net_name + "_avg_bw.csv"
    bw = open(fname, 'w')

    f2name = net_name + "_max_bw.csv"
    maxbw = open(f2name, 'w')

    f3name = net_name + "_cycles.csv"
    cycl = open(f3name, 'w')

    f4name = net_name + "_detail.csv"
    detail = open(f4name, 'w')

    if single_array == 1:
       bw.write("IFMAP SRAM Size[1],\tFilter SRAM Size[1],\tOFMAP SRAM Size[1],\tConv Layer Num,\tDRAM IFMAP Read BW,\tDRAM Filter Read BW,\tDRAM OFMAP Write BW,\tSRAM [1] Read BW,\tSRAM [1] OFMAP Write BW, \n")
       maxbw.write("IFMAP SRAM Size[1],\tFilter SRAM Size[1],\tOFMAP SRAM Size[1],\tConv Layer Num,\tMax DRAM IFMAP Read BW,\tMax DRAM Filter Read BW,\tMax DRAM OFMAP Write BW,\tMax SRAM Read BW[1],\tMax SRAM OFMAP Write BW[1],\n")
       detailed_log = "Layer," +\
                    "\tDRAM_IFMAP_start,\tDRAM_IFMAP_stop,\tDRAM_IFMAP_bytes," + \
                    "\tDRAM_Filter_start,\tDRAM_Filter_stop,\tDRAM_Filter_bytes," + \
                    "\tDRAM_OFMAP_start,\tDRAM_OFMAP_stop,\tDRAM_OFMAP_bytes," + \
                    "\tSRAM_read_start[1],\tSRAM_read_stop[1],\tSRAM_read_bytes[1]," +\
                    "\tSRAM_write_start[1],\tSRAM_write_stop[1],\tSRAM_write_bytes[1],\n"
    else:
       bw.write("IFMAP SRAM Size[1],\tFilter SRAM Size[1],\tOFMAP SRAM Size[1],IFMAP SRAM Size[2],\tFilter SRAM Size[2],\tOFMAP SRAM Size[2],\tConv Layer Num,\tDRAM IFMAP Read BW,\tDRAM Filter Read BW,\tDRAM OFMAP Write BW,\tSRAM [1] Read BW,\tSRAM [1] OFMAP Write BW,\tSRAM [2] Read BW,\tSRAM [2] OFMAP Write BW, \n")
       maxbw.write("IFMAP SRAM Size[1],\tFilter SRAM Size[1],\tOFMAP SRAM Size[1],\tIFMAP SRAM Size[2],\tFilter SRAM Size[2],\tOFMAP SRAM Size[2],\tConv Layer Num,\tMax DRAM IFMAP Read BW,\tMax DRAM Filter Read BW,\tMax DRAM OFMAP Write BW,\tMax SRAM Read BW[1],\tMax SRAM OFMAP Write BW[1],\tMax SRAM Read BW[2],\tMax SRAM OFMAP Write BW[2],\n")
       detailed_log = "Layer," +\
                    "\tDRAM_IFMAP_start,\tDRAM_IFMAP_stop,\tDRAM_IFMAP_bytes," + \
                    "\tDRAM_Filter_start,\tDRAM_Filter_stop,\tDRAM_Filter_bytes," + \
                    "\tDRAM_OFMAP_start,\tDRAM_OFMAP_stop,\tDRAM_OFMAP_bytes," + \
                    "\tSRAM_write_start[1],\tSRAM_write_stop[1],\tSRAM_write_bytes[1]," +\
                    "\tSRAM_write_start[2],\tSRAM_write_stop[2],\tSRAM_write_bytes[2]," +\
                    "\tSRAM_read_start[1],\tSRAM_read_stop[1],\tSRAM_read_bytes[1]," +\
                    "\tSRAM_read_start[2],\tSRAM_read_stop[2],\tSRAM_read_bytes[2],\n"

    cycl.write("Layer,\tCycles,\t% Utilization,\n")
    detail.write(detailed_log)


    first = True
    
    for row in param_file:
        if first:
            first = False
            continue
            
        elems = row.strip().split(',')
        #print(len(elems))
        
        # Do not continue if incomplete line
        if len(elems) < 9:
            continue

        name = elems[0]
        print("")
        print("Commencing run for " + name)

        ifmap_h = int(elems[1])
        ifmap_w = int(elems[2])

        filt_h = int(elems[3])
        filt_w = int(elems[4])

        num_channels = int(elems[5])
        num_filters = int(elems[6])

        strides = int(elems[7])
        
        ifmap_base  = offset_list[0]
        filter_base = offset_list[1]
        ofmap_base  = offset_list[2]

        if single_array == 1:
           bw_log = str(ifmap_sram_size_first) +",\t" + str(filter_sram_size_first) + ",\t" + str(ofmap_sram_size_first) + ",\t" + name + ",\t"
        else:
           bw_log = str(ifmap_sram_size_first) +",\t" + str(filter_sram_size_first) + ",\t" + str(ofmap_sram_size_first) + ",\t" + str(ifmap_sram_size_second) +",\t" + str(filter_sram_size_second) + ",\t" + str(ofmap_sram_size_second) + ",\t" + name + ",\t"
        max_bw_log = bw_log
        detailed_log = name + ",\t"

        bw_str, detailed_str, util, clk, array_one_used, array_two_used =  \
            tg.gen_all_traces(  array_h_first = array_h_first,
                                array_w_first = array_w_first,
                                array_h_second = array_h_second,
                                array_w_second = array_w_second,
                                single_array = single_array,
                                ifmap_h = ifmap_h,
                                ifmap_w = ifmap_w,
                                filt_h = filt_h,
                                filt_w = filt_w,
                                num_channels = num_channels,
                                num_filt = num_filters,
                                strides = strides,
                                data_flow = data_flow,
                                word_size_bytes = 1,
                                filter_sram_size_first = filter_sram_size_first,
                                ifmap_sram_size_first = ifmap_sram_size_first,
                                ofmap_sram_size_first = ofmap_sram_size_first,
                                filter_sram_size_second = filter_sram_size_second,
                                ifmap_sram_size_second = ifmap_sram_size_second,
                                ofmap_sram_size_second = ofmap_sram_size_second,
                                filt_base = filter_base,
                                ifmap_base = ifmap_base,
                                ofmap_base = ofmap_base,
                                sram_read_trace_file_first= net_name + "_" + name + "_sram0_read.csv",
                                sram_read_trace_file_second= net_name + "_" + name + "_sram1_read.csv",
                                sram_write_trace_file_first= net_name + "_" + name + "_sram0_write.csv",
                                sram_write_trace_file_second= net_name + "_" + name + "_sram1_write.csv",
                                dram_filter_trace_file=net_name + "_" + name + "_dram_filter_read.csv",
                                dram_ifmap_trace_file= net_name + "_" + name + "_dram_ifmap_read.csv",
                                dram_ofmap_trace_file= net_name + "_" + name + "_dram_ofmap_write.csv"
                            )

        bw_log += bw_str
        bw.write(bw_log + "\n")

        detailed_log += detailed_str
        detail.write(detailed_log + "\n")

        if single_array == 1:
           both_array_used = 0
           array_two_idle = 0
           array_one_idle = 0
        else:
           both_array_used = 1

           if array_two_used == 1:
              array_two_idle = 0
           else:
              array_two_idle = 1

           if array_one_used == 1:
              array_one_idle = 0
           else:
              array_one_idle = 1

        max_bw_log += tg.gen_max_bw_numbers(
                                both_array_used = both_array_used,
                                array_one_idle = array_one_idle,
                                array_two_idle = array_two_idle,
                                sram_read_trace_file_first = net_name + "_" + name + "_sram0_read.csv", #Selvaraj: Need to update this for two SRAM's after DRAM CSV merge
                                sram_write_trace_file_first= net_name + "_" + name + "_sram0_write.csv",
                                sram_read_trace_file_second = net_name + "_" + name + "_sram1_read.csv",
                                sram_write_trace_file_second= net_name + "_" + name + "_sram1_write.csv",
                                dram_filter_trace_file=net_name + "_" + name + "_dram_filter_read.csv",
                                dram_ifmap_trace_file= net_name + "_" + name + "_dram_ifmap_read.csv",
                                dram_ofmap_trace_file= net_name + "_" + name + "_dram_ofmap_write.csv"
                                )

        maxbw.write(max_bw_log + "\n")

        # Anand: This is not needed, sram_traffic() returns this
        #last_line = subprocess.check_output(["tail","-1", net_name + "_" + name + "_sram_write.csv"] )
        #clk = str(last_line).split(',')[0]
        #clk = str(clk).split("'")[1]

        util_str = str(util)
        line = name + ",\t" + clk +",\t" + util_str +",\n"
        cycl.write(line)

    bw.close()
    maxbw.close()
    cycl.close()
    param_file.close()

#if __name__ == "__main__":
#    sweep_parameter_space_fast()    

