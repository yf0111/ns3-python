import global_configuration as global_c
import numpy as np
from LAHLWNenv import LAHLWNenv
import thesis
from sb3_contrib import TRPO
import csv
import time
import show 

total_time = 0
ue_new_satisfaction = [[0] for i in range(global_c.UE_num)]
ue_old_satisfaction = [[0] for i in range(global_c.UE_num)]

state_avg_ue_outage = [[0] for i in range(global_c.state_num)]
state_avg_ue_new_satisfaction = [[0] for i in range(global_c.state_num)]
state_avg_ue_old_satisfaction = [[0] for i in range(global_c.state_num)]
state_avg_ue_data_rate = [[0] for i in range(global_c.state_num)]
state_avg_jain_fairness_index = [[0] for i in range(global_c.state_num)]

all_avg_ue_outage = [[0] for i in range(global_c.simulation_num)]
all_avg_ue_satisfaction = [[0] for i in range(global_c.simulation_num)]
all_avg_ue_data_rate = [[0] for i in range(global_c.simulation_num)]
all_avg_jain_fairness_index = [[0] for i in range(global_c.simulation_num)]

env = LAHLWNenv()

# # --------------------------------- training model ---------------------------------
# model = TRPO(policy="MlpPolicy",env=env,verbose=1,gamma=0.9,target_kl=0.01)
# model.learn(total_timesteps=1000000) #1000000 for user 10 , 100000 for user 20, 10000 for user 30
# model.get_parameters()
# model.save("trpo_LAHLWN_UE40")
# del model
# # --------------------------------- end of training model ---------------------------

model = TRPO.load("trpo_LAHLWN_UE10")

for simulation in range(global_c.simulation_num):
    start = time.time()
    outage = 0
    satisfaction = 0
    data_rate = 0
    jain = 0
    indoor = 0
    for one in range(global_c.state_num):
        obs = env.reset()
        ue_require = thesis.Thesis.getUEdemand()
        action, _states = model.predict(obs, deterministic=True)
        ue_get = thesis.Thesis.cal_final_data_rate(action=action)
        for i in range(global_c.UE_num):
            if ue_get[i] == 0: # if this ue get is 0 -> assign wifi to ue
                action[i] = 0
        ue_get = thesis.Thesis.cal_final_data_rate(action=action)
        total_outage_num = 0
        for i in range(global_c.UE_num):
            if ue_get[i] < ue_require[i]:
                total_outage_num += 1
        state_avg_ue_outage[one] = total_outage_num / global_c.UE_num
        outage += state_avg_ue_outage[one]

        # cal new satisfaction
        thesis.Thesis.cal_performance(ue_new_satisfaction,ue_old_satisfaction,ue_get,ue_require)
        total_ue_new_satis = 0
        for i in range(global_c.UE_num):
            #total_ue_new_satis += ue_new_satisfaction[i]
            total_ue_new_satis += ue_old_satisfaction[i]
        state_avg_ue_new_satisfaction[one] = total_ue_new_satis / global_c.UE_num
        satisfaction += state_avg_ue_new_satisfaction[one]

        # cal data rate
        total_ue_data_rate = 0
        for i in range(global_c.UE_num):
            total_ue_data_rate += ue_get[i]
        state_avg_ue_data_rate[one] = total_ue_data_rate / global_c.UE_num
        data_rate += state_avg_ue_data_rate[one]

        # cal jain's fairness index
        jain_fairness_top = 0
        jain_fairness_bottom = 0
        for i in range(global_c.UE_num):
            jain_fairness_top += ue_new_satisfaction[i]
            jain_fairness_bottom += pow(ue_new_satisfaction[i],2)
        jain_fairness_top = pow(jain_fairness_top,2)
        jain_fairness_bottom = jain_fairness_bottom * global_c.UE_num
        state_avg_jain_fairness_index[one] = jain_fairness_top / jain_fairness_bottom
        jain += state_avg_jain_fairness_index[one]

        
        thesis.User.orwp()
        thesis.Thesis.allSINR()

    end = time.time()
    all_avg_ue_outage[simulation] = outage / global_c.state_num
    all_avg_ue_satisfaction[simulation] = satisfaction / global_c.state_num
    all_avg_ue_data_rate[simulation] = data_rate / global_c.state_num
    all_avg_jain_fairness_index[simulation] = jain / global_c.state_num

    total_time += (end-start)


# for one in range(global_c.state_num):
#     obs = env.reset()
#     ue_require = thesis.Thesis.getUEdemand()
#     # print("require:",*ue_require)
#     action, _states = model.predict(obs, deterministic=True)
#     # print(action)
#     # obs, reward, done, info = env.step(action)
#     ue_get = thesis.Thesis.cal_final_data_rate(action=action)
#     # print("get:",*ue_get,"\n")
#     for i in range(global_c.UE_num):
#         if ue_get[i] == 0: # if this ue get is 0 -> assign wifi to ue
#             action[i] = 0
#     ue_get = thesis.Thesis.cal_final_data_rate(action=action)
#     # print("reallocate get:",*ue_get,"\n")
    
#     # cal outage
#     total_outage_num = 0
#     for i in range(global_c.UE_num):
#         if ue_get[i] < ue_require[i]:
#             total_outage_num += 1
#     state_avg_ue_outage[one] = total_outage_num / global_c.UE_num

#     # cal new satisfaction
#     thesis.Thesis.cal_performance(ue_new_satisfaction,ue_old_satisfaction,ue_get,ue_require)
#     total_ue_new_satis = 0
#     for i in range(global_c.UE_num):
#         total_ue_new_satis += ue_new_satisfaction[i]
#     state_avg_ue_new_satisfaction[one] = total_ue_new_satis / global_c.UE_num

#     # cal data rate
#     total_ue_data_rate = 0
#     for i in range(global_c.UE_num):
#         total_ue_data_rate += ue_get[i]
#     state_avg_ue_data_rate[one] = total_ue_data_rate / global_c.UE_num
            
    


with open('output.csv','w',newline='') as csvfile:
    writer = csv.writer(csvfile,delimiter=',')
    for i in range(global_c.simulation_num):
        writer.writerow([all_avg_ue_outage[i],all_avg_ue_satisfaction[i],all_avg_ue_data_rate[i],all_avg_jain_fairness_index[i]])


print("per simulation 執行時間：", total_time/global_c.state_num ,"秒")
