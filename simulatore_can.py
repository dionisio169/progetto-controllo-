import can
import time
import threading
import random

# === Nodo motore ===
def motor_node(bus):
    speed = 0
    power = 50  # default power 50%
    running = False

    while True:
        message = bus.recv(timeout=1)
        if message:
            if message.arbitration_id == 0x101:
                command = message.data[0]

                if command == 0x01:
                    running = True
                    print("[MOTORE] Ricevuto comando: START")

                elif command == 0x02 and len(message.data) >= 2:
                    speed = message.data[1]
                    print(f"[MOTORE] Imposta velocità a {speed}")

                elif command == 0x03:
                    running = False
                    speed = 0
                    print("[MOTORE] Ricevuto comando: STOP")

                elif command == 0x04 and len(message.data) >= 2:
                    power = message.data[1]
                    print(f"[MOTORE] Potenza impostata a {power}%")

                # Risposta con stato simulato
                status = can.Message(
                    arbitration_id=0x201,
                    data=[
                        speed,              # Velocità
                        random.randint(20, 80),  # Temperatura
                        power               # Potenza attuale
                    ],
                    is_extended_id=False
                )
                bus.send(status)
        else:
            break

# === Nodo controller ===
def controller_node(bus):
    # START
    bus.send(can.Message(arbitration_id=0x101, data=[0x01], is_extended_id=False))
    time.sleep(1)

    # Imposta velocità
    bus.send(can.Message(arbitration_id=0x101, data=[0x02, 60], is_extended_id=False))
    time.sleep(1)

    # Imposta potenza a 75%
    bus.send(can.Message(arbitration_id=0x101, data=[0x04, 75], is_extended_id=False))
    time.sleep(1)

    # Ferma il motore
    bus.send(can.Message(arbitration_id=0x101, data=[0x03], is_extended_id=False))
    time.sleep(1)

    # Legge stato
    for _ in range(3):
        msg = bus.recv(timeout=1)
        if msg and msg.arbitration_id == 0x201:
            print(f"[CONTROLLER] Stato motore - Velocità: {msg.data[0]}, Temp: {msg.data[1]}, Potenza: {msg.data[2]}%")
        time.sleep(0.5)

# === Main ===
with can.Bus(interface='virtual') as bus:
    motor_thread = threading.Thread(target=motor_node, args=(bus,))
    motor_thread.start()

    controller_node(bus)

    motor_thread.join()

