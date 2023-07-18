import global_configuration as global_c
import thesis
import gym
import channel
from gym import spaces
import numpy as np
import random
import matplotlib.pyplot as plt

state_list = []
action_list = []
now_ap_association = []

# action space
# SAP : 0~4 , total:5
# LA : 0~8, total:9
# action -> 應該要是 [1 x UE_num] 的形式
# 0 : means that this UE connected to WiFi
# 1 : means that this UE connected to LiFi0
# 2 : means that this UE connected to LiFi1
# 3 : means that this UE connected to LiFi2
# 4 : means that this UE connected to LiFi3
# 5 : means that this UE connected to WiFi and LiFi0
# 6 : means that this UE connected to WiFi and LiFi1
# 7 : means that this UE connected to WiFi and LiFi2
# 8 : means that this UE connected to WiFi and LiFi3


class LAHLWNenv(gym.Env):
    def __init__(self):
        super(LAHLWNenv,self).__init__()
        self.currstep = 1 # current step (index)

        self.action_space = spaces.MultiDiscrete(np.array([9,9,9,9,5,5,5,5,5,5])) # UE_num = 10; LA,LA,LA,LA,SAP....
        # self.action_space = spaces.MultiDiscrete(np.array([9,9,9,9,9,9,9,9,5,5,5,5,5,5,5,5,5,5,5,5])) # UE_num = 20; LA,LA,LA,LA,LA,LA,LA,LA,SAP....
        # self.action_space = spaces.MultiDiscrete(np.array([9,9,9,9,9,9,9,9,9,9,9,9,5,5,5,5,5,5,5,5,5,5,5,5,5,5,5,5,5,5])) # UE_num = 30;
        # self.action_space = spaces.MultiDiscrete(np.array([9,9,9,9,9,9,9,9,9,9,9,9,9,9,9,9,5,5,5,5,5,5,5,5,5,5,5,5,5,5,5,5,5,5,5,5,5,5,5,5])) # UE_num = 40;
        # self.action_space = spaces.MultiDiscrete(np.array([9,9,9,9,9,9,9,9,9,9,9,9,9,9,9,9,9,9,9,9,5,5,5,5,5,5,5,5,5,5,5,5,5,5,5,5,5,5,5,5,5,5,5,5,5,5,5,5,5,5])) # UE_num = 50;
        
        self.observation_space = spaces.Box(low = 0, high = 1e10, shape=(global_c.UE_num + global_c.UE_num + global_c.UE_num + global_c.RF_AP_num + global_c.VLC_AP_num,), dtype=np.float32)

    def step(self, action):
        done = False
        self.currstep += 1
        
        ap_associated_matrix = thesis.Thesis.action_to_AP_association_matrix(action=action)
        channel.Channel.updateAllvlcSINR(VLC_SINR_matrix=thesis.VLC_SINR_matrix,VLC_LOS_matrix=thesis.VLC_LOS_matrix,AP_association_matrix=ap_associated_matrix)
        new_state = thesis.Thesis.createState(action=action)
        state_list.append(new_state)
        action_list.append(action)
        ue_require = thesis.Thesis.getUEdemand()
        # reward = thesis.Thesis.calculateR1(state=state_list[len(state_list)-1],prestate=state_list[len(state_list)-2],action=action_list[len(action_list)-1],preaction=action_list[len(action_list)-2]) # R1
        # reward = thesis.Thesis.calculateR2(state=state_list[len(state_list)-1],prestate=state_list[len(state_list)-2],action=action_list[len(action_list)-1],preaction=action_list[len(action_list)-2],ue_require=ue_require) # R2
        reward = thesis.Thesis.calculateR3(state=state_list[len(state_list)-1],prestate=state_list[len(state_list)-2],action=action_list[len(action_list)-1],preaction=action_list[len(action_list)-2],ue_require=ue_require) # R3
        # print("state:",new_state," reward:",reward)
        info = {}
        if self.currstep > 1000:
            done = True

        return new_state,reward,done,info

    def reset(self):
        state_list.clear()
        action_list.clear()
        thesis.Thesis.init()
        thesis.Thesis.allSINR()
        action = [-1 for i in range(global_c.UE_num)]
        new_state = thesis.Thesis.createState(action)
        action_list.append(action)
        state_list.append(new_state)
        return new_state

