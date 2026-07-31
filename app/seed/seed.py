"""
Run once to populate sample quizzes and questions.
Usage:
    python seed.py
"""

import asyncio
from datetime import datetime
from zoneinfo import ZoneInfo

from dotenv import load_dotenv

from app.database import AsyncSessionLocal, init_db
from app.models.quiz import Quiz, Question, DifficultyLevel, QuizType

load_dotenv()

IST = ZoneInfo("Asia/Kolkata")


def now_ist():
    # Return timezone-naive IST datetime
    return datetime.now(IST).replace(tzinfo=None)


async def seed_part1_concepts(db):
    quiz = Quiz(
        title="Embedded Systems & IoT - Part 1 Concepts",
        description="MCQs covering Embedded Systems fundamentals, ESP32 specifications, pins, basic Arduino functions, and sensors.",
        difficulty=DifficultyLevel.easy,
        subject="Embedded Systems & IoT",
        topic="ESP32 Basics and Sensors",
        quiz_type=QuizType.live.value,
        is_active=True,
    )

    quiz.questions.extend([
        Question(
            text="What is an embedded system?",
            options=[
                "A computer used only for gaming",
                "A combination of hardware and software designed for a specific function",
                "A web application",
                "A database system"
            ],
            correct_option=1,
            explanation="An embedded system integrates dedicated hardware and software to perform a specific dedicated task."
        ),
        Question(
            text="What is the main difference between a microcontroller and a microprocessor?",
            options=[
                "Microcontrollers only contain a CPU",
                "Microcontrollers integrate CPU, memory and I/O on a single chip",
                "Microprocessors always consume less power",
                "Microprocessors cannot run programs"
            ],
            correct_option=1,
            explanation="Microcontrollers integrate processor core, memory, and programmable peripherals onto a single integrated circuit."
        ),
        Question(
            text="What is the maximum CPU clock speed mentioned for the ESP32?",
            options=["80 MHz", "120 MHz", "240 MHz", "480 MHz"],
            correct_option=2,
            explanation="The ESP32 dual-core CPU can run up to 240 MHz."
        ),
        Question(
            text="Which wireless technologies are built into the ESP32?",
            options=[
                "Wi-Fi and Bluetooth",
                "Zigbee and GSM",
                "Ethernet and GSM",
                "NFC and Ethernet"
            ],
            correct_option=0,
            explanation="ESP32 natively integrates both Wi-Fi and Bluetooth (including BLE)."
        ),
        Question(
            text="What is the typical operating voltage of the ESP32?",
            options=["1.2 V", "3.3 V", "5 V", "12 V"],
            correct_option=1,
            explanation="The standard operating voltage range for ESP32 ICs is around 3.3V."
        ),
        Question(
            text="How many bits is the ESP32 ADC?",
            options=["8-bit", "10-bit", "12-bit", "16-bit"],
            correct_option=2,
            explanation="ESP32 features 12-bit Successive Approximation Register (SAR) ADCs."
        ),
        Question(
            text="Which communication protocol is NOT listed as an ESP32 communication interface in the PPT?",
            options=["UART", "SPI", "I²C", "HDMI"],
            correct_option=3,
            explanation="HDMI is a display protocol, not a standard embedded communication peripheral like UART, SPI, or I2C."
        ),
        Question(
            text="Which Arduino function runs once when the ESP32 starts?",
            options=["loop()", "setup()", "start()", "mainLoop()"],
            correct_option=1,
            explanation="setup() runs once when the board powers up or resets."
        ),
        Question(
            text="What is the purpose of pinMode(led, OUTPUT)?",
            options=[
                "To read the LED value",
                "To configure the LED pin as an output",
                "To turn the LED ON",
                "To turn the LED OFF"
            ],
            correct_option=1,
            explanation="pinMode() configures the specified pin to behave as an INPUT or OUTPUT."
        ),
        Question(
            text="Which function is used to turn a digital output HIGH or LOW?",
            options=["digitalWrite()", "digitalRead()", "analogRead()", "pinMode()"],
            correct_option=0,
            explanation="digitalWrite() drives a digital pin HIGH (3.3V/5V) or LOW (0V)."
        ),
        Question(
            text="Consider: digitalWrite(19, HIGH); delay(1000); digitalWrite(19, LOW); delay(1000); Approximately how long is one complete ON-OFF cycle?",
            options=["1 second", "2 seconds", "500 ms", "1000 seconds"],
            correct_option=1,
            explanation="1000 ms ON + 1000 ms OFF = 2000 ms total, which equals 2 seconds."
        ),
        Question(
            text="What does the DHT11 sensor measure?",
            options=[
                "Distance and speed",
                "Gas concentration and voltage",
                "Temperature and humidity",
                "Light intensity and pressure"
            ],
            correct_option=2,
            explanation="DHT11 is a digital temperature and humidity sensor."
        ),
        Question(
            text="Which statement correctly compares the IR and ultrasonic sensors shown in the PPT?",
            options=[
                "Both measure temperature",
                "IR uses infrared radiation, while ultrasonic uses sound waves",
                "IR uses sound waves, while ultrasonic uses infrared radiation",
                "Both require an analog input"
            ],
            correct_option=1,
            explanation="IR sensors transmit/detect infrared light waves, whereas Ultrasonic sensors transmit high-frequency sound waves."
        ),
        Question(
            text="Which sensor is the most appropriate for automatically turning on a fan when the room temperature becomes high?",
            options=["IR sensor", "Ultrasonic sensor", "DHT11", "Voltage sensor"],
            correct_option=2,
            explanation="The DHT11 measures temperature, making it suitable for temperature-controlled automation."
        ),
        Question(
            text="Which combination is correctly matched?",
            options=[
                "DHT11 -> Distance",
                "Ultrasonic -> Gas concentration",
                "Gas sensor -> Gas presence/concentration",
                "Relay -> Temperature measurement"
            ],
            correct_option=2,
            explanation="Gas sensors evaluate chemical species/gases in the environment."
        ),
        Question(
            text="What is the key reason a relay is useful in an IoT automation system?",
            options=[
                "It directly measures electrical current",
                "It allows a low-voltage controller signal to control a higher-power load",
                "It provides Wi-Fi connectivity",
                "It converts analog signals into digital signals"
            ],
            correct_option=1,
            explanation="Relays act as electrically operated switches to control AC or high DC current circuits using low power GPIO signals."
        ),
        Question(
            text="If a Blynk switch sends 1 through V2, what happens in the given program?",
            options=[
                "LED is turned OFF",
                "LED pin is configured as INPUT",
                "LED is driven HIGH",
                "ESP32 disconnects from Wi-Fi"
            ],
            correct_option=2,
            explanation="Receiving a '1' logic high from Blynk drives the connected pin HIGH."
        ),
        Question(
            text="Which GPIO pin is most commonly connected to the onboard/built-in LED on standard ESP32 development boards?",
            options=["GPIO 0", "GPIO 2", "GPIO 13", "GPIO 16"],
            correct_option=1,
            explanation="GPIO 2 is tied to the built-in blue LED on most standard ESP32 boards (like NodeMCU-32S)."
        ),
        Question(
            text="A student uses Serial.begin(115200) in the Wi-Fi example. What is the primary purpose of this statement?",
            options=[
                "Set the Wi-Fi frequency",
                "Set the Serial communication baud rate",
                "Set the ADC resolution",
                "Set the CPU clock speed"
            ],
            correct_option=1,
            explanation="Serial.begin() initializes serial transmission and sets the communication speed in baud (bits per second)."
        ),
        Question(
            text="If the Serial Monitor baud rate does not match the baud rate used in Serial.begin(), what is the most likely problem?",
            options=[
                "The ESP32 hardware will be permanently damaged",
                "The displayed serial output may appear corrupted or unreadable",
                "The sensor will automatically stop measuring",
                "The relay will always remain ON"
            ],
            correct_option=1,
            explanation="Mismatched baud rates prevent proper UART clock synchronization, leading to garbage/unreadable output."
        ),
        Question(
            text="What is the purpose of a gas sensor?",
            options=[
                "To measure distance",
                "To detect gases such as methane, LPG or carbon monoxide",
                "To control an LED",
                "To measure humidity"
            ],
            correct_option=1,
            explanation="Gas sensors detect airborne chemical components or gaseous fuels."
        ),
        Question(
            text="Which voltage regulator provides 3.3 V?",
            options=["7805", "LD33V", "LM358", "7812"],
            correct_option=1,
            explanation="LD33V is a 3.3V fixed low-dropout (LDO) linear regulator."
        ),
        Question(
            text="What is Blynk used for in the presented IoT system?",
            options=[
                "Compiling C programs",
                "Creating an IoT dashboard and monitoring/control of devices",
                "Programming only Arduino Uno",
                "Designing PCBs"
            ],
            correct_option=1,
            explanation="Blynk provides mobile and web dashboard frameworks to control connected hardware."
        ),
        Question(
            text="In Blynk, what is a Datastream primarily used for?",
            options=[
                "Storing the ESP32 firmware",
                "Defining how data is exchanged between the device and Blynk",
                "Connecting the ESP32 to USB",
                "Programming the DHT11"
            ],
            correct_option=1,
            explanation="Datastreams channel numeric, string, or virtual parameters between the physical board and virtual widgets."
        ),
        Question(
            text="Which function is used to send sensor values to a Blynk virtual pin?",
            options=[
                "Blynk.send()",
                "Blynk.virtualWrite()",
                "Blynk.writeSensor()",
                "Blynk.sendData()"
            ],
            correct_option=1,
            explanation="Blynk.virtualWrite(vPin, value) updates data on the specified virtual pin."
        ),
    ])

    db.add(quiz)
    await db.commit()
    print("✅ Part 1 Concepts seeded successfully.")


async def seed_part2_concepts(db):
    quiz = Quiz(
        title="C Programming - Part 2 Concepts",
        description="Execution workflow, flowcharts, identifiers, conditionals, switch cases, and keywords in C.",
        difficulty=DifficultyLevel.easy,
        subject="Programming",
        topic="C Programming Basics",
        quiz_type=QuizType.live.value,
        is_active=True,
    )

    quiz.questions.extend([
        Question(
            text="What is the correct sequence for executing a C program?",
            options=[
                ".c -> CPU Compiler -> .exe -> Output",
                ".c -> Compiler -> .exe -> CPU -> Output",
                ".c -> .exe -> Compiler -> CPU -> Output",
                ".c -> CPU -> .exe -> Compiler -> Output"
            ],
            correct_option=1,
            explanation="Source code (.c) gets compiled into executable binary (.exe), which is then run by the CPU to produce output."
        ),
        Question(
            text="Which flowchart symbol is used to represent a decision?",
            options=["Rectangle", "Oval", "Diamond", "Parallelogram"],
            correct_option=2,
            explanation="In flowcharts, diamonds represent decision-making nodes (e.g., condition checks)."
        ),
        Question(
            text="Which of the following is a valid C identifier?",
            options=["2marks", "student-name", "total_marks", "float"],
            correct_option=2,
            explanation="Identifiers cannot start with numbers, contain hyphens, or use reserved keywords. 'total_marks' is valid."
        ),
        Question(
            text="What will be the output of this code?\nint x = 10;\nif (x > 5) {\n    printf(\"A\");\n} else {\n    printf(\"B\");\n}",
            options=["A", "B", "AB", "No output"],
            correct_option=0,
            explanation="Since x = 10, the condition (10 > 5) is true, executing the first branch to print 'A'."
        ),
        Question(
            text="Consider:\nint day = 3;\nswitch(day) {\n    case 1: printf(\"Monday\"); break;\n    case 3: printf(\"Wednesday\"); break;\n    default: printf(\"Invalid\");\n}\nWhat is the output?",
            options=["Monday", "Tuesday", "Wednesday", "Invalid"],
            correct_option=2,
            explanation="The value of day is 3, matching 'case 3:' which prints 'Wednesday'."
        ),
        Question(
            text="Why is &age used in the following statement?\nint age;\nscanf(\"%d\", &age);",
            options=[
                "& converts age into a string",
                "& provides the address where scanf() should store the input",
                "& prints the value of age",
                "& makes age a constant"
            ],
            correct_option=1,
            explanation="The address-of operator (&) passes the memory address of the variable so scanf can write the value into it."
        ),
        Question(
            text="Which declaration is invalid according to the identifier rules?",
            options=["student_name", "_marks", "student2", "2student"],
            correct_option=3,
            explanation="Identifiers in C cannot begin with a numeric digit."
        ),
        Question(
            text="What is the key difference between age, Age, and AGE in C?",
            options=[
                "They represent the same variable",
                "Only age is valid",
                "C treats them as different identifiers",
                "Only uppercase identifiers are allowed"
            ],
            correct_option=2,
            explanation="C is a case-sensitive programming language, treating distinct letter cases as distinct identifiers."
        ),
        Question(
            text="Which statement about the following is correct?\nconst int MAX_USERS = 100;",
            options=[
                "MAX_USERS can later be changed to 200",
                "MAX_USERS is a variable that changes automatically",
                "MAX_USERS cannot be modified during program execution",
                "const means the value is stored in a string"
            ],
            correct_option=2,
            explanation="The 'const' qualifier marks a variable as read-only once initialized."
        ),
        Question(
            text="What is wrong with this declaration?\nint float = 10;",
            options=[
                "10 cannot be assigned to an integer",
                "float is a reserved keyword and cannot be used as an identifier",
                "int cannot store numbers",
                "Nothing is wrong"
            ],
            correct_option=1,
            explanation="'float' is a reserved data type keyword in C and cannot be repurposed as a variable identifier."
        ),
    ])

    db.add(quiz)
    await db.commit()
    print("✅ Part 2 Concepts seeded successfully.")


async def seed():
    await init_db()

    async with AsyncSessionLocal() as db:
        try:
            await seed_part1_concepts(db)
            await seed_part2_concepts(db)

            print("🚀 Seed process completed successfully!")
        except Exception as e:
            await db.rollback()
            print(f"❌ Error during seeding: {e}")
            raise


if __name__ == "__main__":
    asyncio.run(seed())