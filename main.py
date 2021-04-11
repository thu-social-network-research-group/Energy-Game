import numpy as np
from electricity import Electricity
from scipy.optimize import minimize
from hyper import *
from matplotlib import pyplot as plt

e = Electricity(N, H)

for day in range(T):
    print('Day:', day)
    try:
        while True:
            print('-' * 50)
            price, time = e.set_price_t(g)
            print('Hour:', time)
            print('Price:', price)
            for u in range(N):
                print('User:', u)
                print('Strategy_x:', e.user_list[u].x_user[time])
                print('Strategy_s:', e.user_list[u].s_user[time])
                print('Schedule_x:', e.user_list[u].x_sch[time])

                fun = e.user_list[u].sum_cost_t
                print('Sum_cost:', fun(e.user_list[u].x_user[time].tolist() + [e.user_list[u].s_user[time]]))

                print([e.user_list[u].is_used()[i] for i in range(e.user_list[u].x_user[time].shape[0])])
                print('Power supplied:', not e.is_not_power())

                cons = (
                    # x_user = 0 when appliance does not work
                    {'type': 'eq',
                     'fun': lambda x: x[np.where(e.user_list[u].is_used() == 0)]},
                    # x_user >= Pmin when appliance works
                    {'type': 'ineq',
                     'fun': lambda x: x[:-1][np.where(e.user_list[u].is_used() == 1)] - epsilon - Pmin},
                    # x_user <= Pmax when appliance works
                    {'type': 'ineq',
                     'fun': lambda x: - x[:-1][np.where(e.user_list[u].is_used() == 1)] - epsilon + Pmax},
                    # s_user >= 0 when electricity is supplied
                    {'type': 'ineq',
                     'fun': lambda x: (x[-1] - epsilon) if not e.is_not_power() else 1},
                    # s_user >= -Vmax
                    {'type': 'ineq',
                     'fun': lambda x: x[-1] - epsilon + Vmax},
                    # sum(x_user) + s_user = 0 when electricity is not supplied
                    {'type': 'eq',
                     'fun': lambda x: (np.sum(x) - epsilon) if e.is_not_power() else 1},
                    # sum(s_user) ≈ 0
                    # {'type': 'ineq',
                    #  'fun': lambda x: x[-1] + e.user_list[u].s_user[time - 1] + Smax - epsilon},
                )

                res = minimize(fun, e.user_list[u].x_user[time].tolist() + [e.user_list[u].s_user[time]],
                               method='SLSQP', constraints=cons, tol=1e-6, options={'disp': True})
                x_new, s_new = res.x[:-1], res.x[-1]
                print('x_new:', x_new)
                print('s_new:', s_new)
                e.user_list[u].change(x_new, s_new)

    except StopIteration:
        e.reset_time(H)
        print('=' * 50)
