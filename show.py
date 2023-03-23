import global_configuration as global_c

class Show:
    def __init__(self):
        pass
    
    @staticmethod
    def printVLCLOS(vlc_los_matrix):
        print("VLC LOS matrix as below : \n")
        for AP_index in range(global_c.RF_AP_num + global_c.VLC_AP_num):
            print("for VLC AP ",AP_index)
            for UE_index in range(global_c.UE_num):
                print("UE ",UE_index," : ",vlc_los_matrix[AP_index-1][UE_index-1],"\n")

