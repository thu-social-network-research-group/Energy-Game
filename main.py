import numpy as np
from scipy.optimize import minimize
from hyper import *

np.random.seed(42)


class User:
    def __init__(self, h, a, w=None, x_user=None, x_sch=None, s_user=None):
        """
        :param h: Total number of hours a day
        :param a: Total number of the user's appliance
        :param w: Coefficient of preference
        :param x_user: Electricity consumption of the user
        :param x_sch: Scheduled electricity consumption of the user
        :param s_user: Storage consumption of the user
        """
        self.price = 1
        self.time = 0
        self.num_appliance = a
        if w is None:
            self.w = np.random.random(a)
        else:
            self.w = w
        if x_user is None:
            self.x_user = np.random.random((h, a))
        else:
            self.x_user = x_user
        if x_sch is None:
            self.x_sch = np.random.random((h, a))
        else:
            self.x_sch = x_sch
        if s_user is None:
            self.s_user = np.random.random(h)
        else:
            self.s_user = s_user

    def change(self, x_user_new, s_user_new):
        """
        Change the user's strategy
        :param x_user_new: New electricity consumption
        :param s_user_new: New storage consumption
        """
        self.x_user[self.time] = x_user_new
        self.s_user[self.time] = s_user_new

    def is_unchanged(self, x_user_new, s_user_new):
        """
        Judge if there is a change
        :param x_user_new: New electricity consumption
        :param s_user_new: New storage consumption
        :return: If there is a change
        """
        return np.all(self.x_user - epsilon <= x_user_new <= self.x_user + epsilon) and np.all(
            self.s_user - epsilon <= s_user_new <= self.s_user + epsilon)

    def charge_t(self):
        """
        Calculate the user's electric charge of time t
        :return: electric charge
        """
        return self.price * (self.x_user[self.time] + self.s_user[self.time]) \
            / (np.sum(self.x_user) + np.sum(self.s_user))

    def discomfort_t(self):
        """
        Calculate the user's discomfort of time t
        :return: discomfort
        """
        return np.sum(np.multiply(self.w, (self.x_user[self.time] - self.x_sch[self.time]) ** 2))

    def sum_cost_t(self, x):
        """
        Calculate the user's total cost of time t
        :return:
        """
        if x[0] is None or x[1] is None:
            return self.price * (self.x_user[self.time] + self.s_user[self.time]) \
                / (np.sum(self.x_user) + np.sum(self.s_user)) \
                + np.sum(np.multiply(self.w, (self.x_user[self.time] - self.x_sch[self.time]) ** 2))
        else:
            return self.price * (x[0] + x[1]) / (np.sum(self.x_user) + np.sum(self.s_user)) \
                + np.sum(np.multiply(self.w, (x[0] - self.x_sch[self.time]) ** 2))


class Electricity:
    def __init__(self, n, l=None):
        """
        :param n: Number of users
        :param l: List of users
        """
        self.time = np.arange(H).__iter__()
        if l is None:
            self.user_list = [User(H, np.random.randint(3, 7)) for _ in range(n)]
        else:
            self.user_list = l

    def set_price_t(self):
        """
        Calculate the price of the electricity
        :return: price (P(t)=g*Lt^2)
        """
        time = self.time.__next__()
        print('Hour:', time)
        total = 0
        for i in range(len(self.user_list)):
            total += np.sum(self.user_list[i].x_user[time]) + self.user_list[i].s_user[time]
            self.user_list[i].time = time
            self.user_list[i].price = g * total ** 2
        return g * total ** 2

    def reset_time(self):
        self.time = np.arange(H).__iter__()


if __name__ == "__main__":
    e = Electricity(N)

    for _ in range(10):  # Iteration times
        print('Day:', _)
        try:
            while True:
                e.set_price_t()
                for u in range(N):
                    res = minimize(e.user_list[u].sum_cost_t, [100, 100],
                                   method='nelder-mead', options={'xtol': 1e-2, 'disp': True})
                    [x_new, s_new] = res.x
                    print('User:', u)
                    print('x_new:', x_new, 's_new:', s_new)
                    e.user_list[u].change(x_new, s_new)

                pass  # TODO: Optimization Algorithm

        except StopIteration:
            e.reset_time()
            print('-' * 10)
