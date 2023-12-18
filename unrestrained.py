import numpy as np
import cv2
import math
import matplotlib.pyplot as plt

MARGIN = 5
numbers = True
#930, 31, 32
nrange = range(99, 100)
visualize = len(nrange) < 5 and max(nrange) < 200
plotmode = len(nrange) > 20
skiptest = True
# 9863
if plotmode:
    diff_list = list()
for n in nrange:
    An = n * (n + 1) * (2 * n + 1) / 6
    N = math.sqrt(An)
    LB0 = math.ceil(N)
    n_itr = n
    acc = 0
    nsum = 0
    ncur = n
    while nsum < (N - n):
        nsum += ncur
        ncur -= 1
    if nsum + ncur < N + 0.5 * n:
        c_ = 1 - ((nsum + ncur - N - 1)/N)
    else:
        c_ = 1 - ((nsum - N - 1) / N)
    c_ = round(c_, 3)
    N1 = N - (n * (1 - c_))
    N2 = N + (n * (1 - c_))
    #print(N1, N2)
    # ((-2 * sqrt(x * (x + 1) * (2 * x + 1) / 6) + sqrt(pow(2 * sqrt(x * (x + 1) * (2 * x + 1) / 6), 2) + 4 * pow((1 - 7/8), 2))) / 2)
    # ->    0
    r_n = math.ceil((-2 * N + math.sqrt(pow(2 * N, 2) + 4 * pow((1 - c_), 2))) / 2)
    #print(r_n)
    N1 = math.ceil(N1 + r_n)
    N2 = math.ceil(N2 + r_n)

    #print(N1 * N2)
    #print(An)
    N1 += MARGIN
    N2 += MARGIN
    width = N1 + n
    height = math.ceil(N2 + c_ * n)
    if visualize:
        img = np.zeros((height + 2 * MARGIN + 100, width + 2 * MARGIN + 100, 3), np.uint8)
    x_coord = MARGIN
    y_coord = MARGIN
    x_max = x_coord
    y_max = y_coord
    if visualize:
        cv2.rectangle(img, (x_coord, y_coord), (N1 + x_coord, N2 + y_coord), (255, 255, 255), 1)
        cv2.rectangle(img, (x_coord, y_coord), (width + x_coord, height + y_coord), (0, 0, 255), 1)
    n_itr = n
    n_itr_other = n
    n_itr_backup = n
    prev_H = [0, 0]
    H = 0
    prev_n = n
    prev_N1 = N1
    prev_N2 = N2
    dir = 0 # horizontal filling is 0, vertical is 1
    wiggle = 1 # left to right is 1, right to left is -1
    swapped = 1
    # In Phase 1 we deal with the squares of size i in the range n/2 − x < i ≤ n, for a relatively small x
    # This procedure terminates when also the rectangle R m containing the square floor(n/2) + 1 is packed up to at least N1.
    while n_itr > 0:
        while n_itr > prev_n/2:
            while ((1 - dir) * x_coord + min(wiggle, 0) <= prev_N1) and (dir * y_coord <= prev_N2):
                if visualize:
                    cv2.rectangle(img, (x_coord, y_coord), (x_coord + n_itr, y_coord + n_itr), (0, 255, 0), 1)
                if n_itr > 20 and visualize and numbers:
                    cv2.putText(img, str(n_itr), (x_coord + int(n_itr/2.5), y_coord + int(n_itr/2)), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 255, 0), 1, 2)
                x_coord += (1 - dir) * n_itr * wiggle
                y_coord += (dir) * n_itr * wiggle
                x_max = max(x_max, x_coord)
                y_max = max(y_max, y_coord + n_itr)
                # due to n_itr decrementation happening after this, we only need to make space for one smaller square than n_itr
                if wiggle < 0:
                    y_coord += 1
                    x_coord += 1
                n_itr -= 1
                if n_itr == 0:
                    break
                if x_coord < MARGIN or y_coord < MARGIN:
                    break

            y_coord += (1 - dir) * (n_itr)
            x_coord += dir * (n_itr + 1)
            #print(n_itr * wiggle)
            wiggle = -wiggle
            if wiggle < 0:
                y_coord += 1
                x_coord -= 1
            if n_itr:
                n_itr_other = n_itr
                if wiggle > 0:
                    n_itr_backup = n_itr
            if dir:
                y_coord = y_coord + wiggle * (n_itr_other - 1)
            else:
                x_coord = wiggle < 0 and x_coord + wiggle * (n_itr_other - 1) or MARGIN
        prev_H[swapped ^ dir] = H
        #if swapped:
        H = dir * x_coord + (1 - dir) * y_coord - MARGIN
        #else:a
        #    H += dir * x_coord + (1 - dir) * y_coord - MARGIN
        prev_n = n_itr
        # If N1 ≤ N2 − H holds, then Phase 2 continues the procedure with horizontal edge-to-edge cuts exactly in the same way as we did in Phase 1
        if prev_N1 <= (prev_N2 - H) or skiptest:
            swapped = 0
            continue
        # Otherwise, if N1 > N2 − H , we switch the roles of the two parameters so that N1' := N2 − H + cn − n′ and N2' := N1 + n − cn′
        N1_ = math.ceil(prev_N2 - H + c_ * n - n_itr)
        N2_ = math.ceil(prev_N1 + n - c_ * n_itr)
        if visualize:
            cv2.rectangle(img, (x_coord, y_coord), (N1_ + y_coord, N2_ + x_coord), (0, 255, 0), 1)
        prev_N1 = N1_
        prev_N2 = N2_
        dir = 1 - dir
        swapped = 1

    Nceil = math.ceil(N)
    guessed_x = x_max - MARGIN
    guessed_y = y_max - MARGIN
    diff = max((guessed_y) - Nceil, (guessed_x - Nceil))
    if not plotmode:
        print(f"for n value {n}: maximum x: {guessed_x}, maximum y: {y_max - MARGIN}, estimated value: {Nceil}, difference: {diff}")
        if guessed_y > guessed_x:
            print(f"largest height of bottom row is {wiggle > 1 and n_itr_backup or n_itr_other}")
        if visualize:
            cv2.rectangle(img, (MARGIN, MARGIN), (guessed_x + MARGIN, guessed_y + MARGIN), (255, 0, 255))
            cv2.imwrite(f"./images/unrestrained_n{n}_c{c_}.png", img)
            cv2.imshow("asd", img)
        cv2.waitKey(0)
if plotmode:
    plt.plot(nrange, diff_list)
    plt.plot(nrange, [n/2 for n in nrange])
    plt.show()