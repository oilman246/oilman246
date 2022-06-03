
#Race Car Start Progam

import machine
import utime
import _thread
from machine import Pin, Timer
import rp2


#Reset all I/O


#Define I/O

global Reset
global Latch
global Fire_1
global Fire_2
global Race_car
global flag
global timer_start
global reaction_1
global reaction_2
global latch_1
global latch_2


flag = 1
Reset = 1
Latch = 1
Fire_1 = 1
Fire_2 = 1
Race_car = 0
latch_1 = 0
latch_2 = 0

# Blink Light

led =Pin(25, Pin.OUT)
tim = Timer()
def tick(timer):
    global led
    led.toggle()
tim.init(freq=2.5, mode=Timer.PERIODIC, callback=tick)

START = 0
Go_1R = 0
Go_1X = 0
Go_2R = 0
Go_2X = 0
START_X = 0

Reset_out = machine.Pin(5, machine.Pin.OUT)
solenoid_1 = machine.Pin(26, machine.Pin.OUT)
solenoid_2 = machine.Pin(27, machine.Pin.OUT)
Light_R = machine.Pin(6, machine.Pin.OUT) # Red light
Light_O = machine.Pin(7, machine.Pin.OUT) # Orange light
Light_B = machine.Pin(8, machine.Pin.OUT) # blue light
Light_G = machine.Pin(9, machine.Pin.OUT) # green light
#Buzzer_L is located on the circuit board used for testing.
#Buzzer_L = machine.Pin(18, machine.Pin.OUT) # PICO buzzer
Buzzer_R = machine.Pin(28, machine.Pin.OUT)
Racer_1 = machine.Pin(3, machine.Pin.OUT)
Racer_2 = machine.Pin(4, machine.Pin.OUT)
#Watch_dog = machine.Pin(25, machine.Pin.OUT) #PICO light

# initialize all lights to off

lights = []
for i in range(18):
    lights.append(machine.Pin(i, machine.Pin.OUT))
for light in lights:
    light.value(0)
solenoid_1.value(1)
solenoid_2.value(1)


# Close solenoid valves(energize to close).
START_X = machine.Pin(0, machine.Pin.IN, machine.Pin.PULL_UP)
START = machine.Pin(20, machine.Pin.IN, machine.Pin.PULL_UP)
Go_1R = machine.Pin(1, machine.Pin.IN, machine.Pin.PULL_DOWN)
Go_2R = machine.Pin(2, machine.Pin.IN, machine.Pin.PULL_DOWN)
Go_1X = machine.Pin(21, machine.Pin.IN, machine.Pin.PULL_DOWN)
Go_2X = machine.Pin(22, machine.Pin.IN, machine.Pin.PULL_DOWN)

#print("START =", START.value())


def input_interrupt():
    while True:
        global Reset
        global Fire_1
        global Fire_2
        global Light_B
        
        
        
        Reset = -(START.value() - 1)
        utime.sleep(.02)
        Fire_1A = Go_1R.value()
        utime.sleep(.02)
        Fire_1B = Go_1X.value()
        utime.sleep(.01)
        Fire_1 = Fire_1A or Fire_1B
        utime.sleep(.01)
        Fire_2A = Go_2R.value()
        utime.sleep(.01)
        Fire_2B = Go_2X.value()
        utime.sleep(.01)
        Fire_2 = Fire_2A or Fire_2B
        utime.sleep(.01)
        Reset_out = Reset
        
_thread.start_new_thread(input_interrupt, ())

def fault_sequence(car):
# Identifies racer who fires too early    
    global Reset
    global Latch
    while Reset == 0:
        
        Buzzer_R.value(1)
        
        solenoid_1.value(1)
        solenoid_2.value(1)
        
        if car == 1:
            Racer_1.value(1)
            utime.sleep(1)
            Racer_1.value(0)
            utime.sleep(1)
            
        if car == 2:
            Racer_2.value(1)
            utime.sleep(1)
            Racer_2.value(0)
            utime.sleep(1)    
        Latch = 0
        
def start_sequence():
# Cycles start lights red to green    
    global Latch
    global Reset
    global flag
    global Fire_1
    global Fire_2
    global timer_start
    while flag == 0:
        @rp2.asm_pio()
        def wait_pin_low():
            wrap_target()
            
            wait(0, pin, 0)
            irq(block, rel(0))
            wait(1, pin, 0)

            wrap()
        
        def handler(sm):
            global latch
            
            if Latch == 1:
                if sm == sm0:
                    fault_sequence(1)
                
                if sm == sm1:
                    fault_sequence(2)
                      
            
        Sequence_T = 2
        Latch = 1
        print("Start Race")
        Light_G.value(0)
        Light_R.value(1)
        utime.sleep(Sequence_T)
        Light_O.value(1)
        Light_R.value(0)
        utime.sleep(Sequence_T)
        Light_B.value(1)
        Light_O.value(0)
        utime.sleep(Sequence_T)
        if Fire_1 == 0:
            fault_sequence(1)
            break
        if Fire_2 == 0:
            fault_sequence(2)
            brea
            
        Light_G.value(1)
        timer_start = utime.ticks_ms()
        Light_B.value(0)
        Latch = 0
        flag = 1
        pin21 = Pin(21, Pin.IN, Pin.PULL_UP)        
        sm0 = rp2.StateMachine(0, wait_pin_low, in_base=pin21)
        sm0.irq(handler)

        pin22 = Pin(22, Pin.IN, Pin.PULL_UP)
        sm1 = rp2.StateMachine(1, wait_pin_low, in_base=pin22)
        sm1.irq(handler)
        
        sm0.active(1)
        sm1.active(1)
    

def fire_sequence():
# Activates the air solenoid valves if light is green
    global Fire_1
    global Fire_2
    global Latch
    global Reset
    global timer_start
    global latch_1
    global latch_2
    while Reset == 0:
        reaction_1 = 0
        reaction_2 = 0
        

        solenoid_1.value(Fire_1)
        
        if Fire_1 == 0 and latch_1 == 0:
            reaction_1 = utime.ticks_diff(utime.ticks_ms(), timer_start)
            Racer_1.value(-(Fire_1-1))
            print("Race Car 1 reaction time " + str(reaction_1) + " milliseconds")
            latch_1 = 1
        solenoid_2.value(Fire_2)
        
        if Fire_2 == 0 and latch_2 == 0:
            reaction_2 = utime.ticks_diff(utime.ticks_ms(), timer_start)
            print("Race Car 2 reaction time " + str(reaction_2) + " milliseconds")
            Racer_2.value(-(Fire_2-1))
            latch_2 = 1
        
        
            
def fault_sequence(car):
    global Reset
    
    while Reset == 0:
#        flasher()
        
        Buzzer_R.value(1)
        if car == 1:
            Racer_1.value(1)
            utime.sleep(1)
            Racer_1.value(0)
            utime.sleep(1)
            
        if car == 2:
            Racer_2.value(1)
            utime.sleep(1)
            Racer_2.value(0)
            utime.sleep(1)    

#Main Program
      
while True:
    global Reset
    global Fire_1
    global Fire_2
    global Latch
    global flag
    global latch_1
    global latch_2
   
           
 #Start the light sequence       
    while Reset == 0:
        global flag
        global reset
        global Fire_1
        global Fire_2
        global Latch
        global latch_1
        global latch_2
        start_sequence()
        fire_sequence()
    
    while Reset == 1:
        global flag
        global reset
        global Fire_1
        global Fire_2
        global Latch
        global latch_1
        global latch_2
        
        solenoid_1.value(1)
        solenoid_2.value(2)
        Buzzer_R.value(0)
        
        Light_R.value(0)
        Light_O.value(0)
        Light_B.value(0)
        Light_G.value(0)
        Racer_1.value(0)
        Racer_2.value(0)
        flag = 0
        Latch = 1
        latch_1 = 0
        latch_2 = 0
        
        
     

                
        
            
        
  


