from flask import Flask, request, jsonify
from collections import deque
import time

app = Flask(__name__)

historyA = deque()
historyB = deque()
EMA_ALPHA = 0.3
emaA = 0
emaB = 0
HISTORY_MAX = 300

def push(deq, v):
    deq.append((time.time(), v))
    while len(deq) > HISTORY_MAX:
        deq.popleft()

def compute_rate(deq):
    if len(deq) < 2:
        return 0
    t0, v0 = deq[0]
    tn, vn = deq[-1]
    dt = tn - t0
    return (vn - v0) / dt if dt > 0 else 0

@app.route("/update", methods=["POST"])
def update():
    global emaA, emaB
    data = request.get_json()
    carsA = int(data["carsA"])
    carsB = int(data["carsB"])

    push(historyA, carsA)
    push(historyB, carsB)

    rateA = compute_rate(historyA)
    rateB = compute_rate(historyB)

    emaA = emaA * (1 - EMA_ALPHA) + rateA * EMA_ALPHA
    emaB = emaB * (1 - EMA_ALPHA) + rateB * EMA_ALPHA

    predA = max(0, emaA * 15)
    predB = max(0, emaB * 15)

    scoreA = carsA + predA
    scoreB = carsB + predB

    if scoreA < 4 and scoreB < 4:
        mode = "both_open"
        timeA = 8
        timeB = 8
    elif scoreA >= 4 and scoreB >= 4:
        mode = "toggle"
        timeA = 15
        timeB = 15
    else:
        if scoreA >= 4:
            mode = "priority_A"
            timeA = 15
            timeB = 0
        else:
            mode = "priority_B"
            timeB = 15
            timeA = 0

    return jsonify({
        "mode": mode,
        "timeA": timeA,
        "timeB": timeB,
        "scoreA": scoreA,
        "scoreB": scoreB
    })

@app.route("/", methods=["GET"])
def home():
    return "AI Traffic Server Running"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
