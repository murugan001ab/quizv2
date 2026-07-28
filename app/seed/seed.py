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
        title="C Programming - Part 1 Concepts",
        description="Introduction to Programming, Algorithm, Flowchart, Structure of C Program, Header Files, main(), Variables, Data Types",
        difficulty=DifficultyLevel.easy,
        subject="Programming",
        topic="Introduction to C",
        quiz_type=QuizType.live.value,
        is_active=True,
    )

    quiz.questions.extend([
        Question(
            text="Which best describes programming?",
            options=[
                "Repairing computer hardware",
                "Giving step-by-step instructions to a computer",
                "Installing operating systems",
                "Typing very fast"
            ],
            correct_option=1,
            explanation="Programming is the process of giving instructions to a computer to perform tasks."
        ),
        Question(
            text="Why do computers need programming?",
            options=[
                "They can think like humans",
                "They automatically know every task",
                "They only follow instructions given by programmers",
                "To increase RAM"
            ],
            correct_option=2,
            explanation="A computer only follows instructions written by programmers."
        ),
        Question(
            text="Which of the following is an algorithm?",
            options=[
                "A recipe for making tea",
                "A movie",
                "A keyboard",
                "A compiler"
            ],
            correct_option=0,
            explanation="A recipe is a step-by-step procedure, just like an algorithm."
        ),
        Question(
            text="An algorithm should always be",
            options=[
                "Random",
                "Step-by-step",
                "Very long",
                "Written only in English"
            ],
            correct_option=1,
            explanation="Algorithms solve problems using a clear sequence of steps."
        ),
        Question(
            text="Which comes before writing a program?",
            options=[
                "Algorithm",
                "Compiler",
                "Execution",
                "Output"
            ],
            correct_option=0,
            explanation="Planning using an algorithm helps before coding."
        ),
        Question(
            text="What is the main purpose of a flowchart?",
            options=[
                "Increase program speed",
                "Visualize program logic",
                "Store variables",
                "Compile programs"
            ],
            correct_option=1,
            explanation="Flowcharts graphically represent the logic of a program."
        ),
        Question(
            text="Which symbol usually represents a decision in a flowchart?",
            options=[
                "Rectangle",
                "Circle",
                "Diamond",
                "Arrow"
            ],
            correct_option=2,
            explanation="A diamond represents a decision or condition."
        ),
        Question(
            text="Which section is mandatory in every C program?",
            options=[
                "scanf()",
                "printf()",
                "main()",
                "switch"
            ],
            correct_option=2,
            explanation="Every C program starts execution from main()."
        ),
        Question(
            text="What is the purpose of header files?",
            options=[
                "Store variables",
                "Provide declarations of predefined functions",
                "Increase memory",
                "Execute the program"
            ],
            correct_option=1,
            explanation="Header files provide declarations for library functions."
        ),
        Question(
            text="Which header file is required for printf() and scanf()?",
            options=[
                "math.h",
                "stdio.h",
                "string.h",
                "stdlib.h"
            ],
            correct_option=1,
            explanation="stdio.h contains standard input and output functions."
        ),
        Question(
            text="Why is main() called the entry point?",
            options=[
                "It prints output",
                "Program execution begins there",
                "It stores variables",
                "It creates header files"
            ],
            correct_option=1,
            explanation="The operating system starts executing a C program from main()."
        ),
        Question(
            text="A variable is used to",
            options=[
                "Repeat loops",
                "Store data",
                "Create flowcharts",
                "Compile code"
            ],
            correct_option=1,
            explanation="Variables store values that can be used and modified."
        ),
        Question(
            text="Which of the following is a valid variable declaration?",
            options=[
                "int age;",
                "int 2age;",
                "int for;",
                "int float;"
            ],
            correct_option=0,
            explanation="Variable names cannot begin with numbers or use keywords."
        ),
        Question(
            text="Which data type stores whole numbers?",
            options=[
                "float",
                "char",
                "int",
                "double"
            ],
            correct_option=2,
            explanation="int stores integer values."
        ),
        Question(
            text="Which data type is suitable for storing a single character?",
            options=[
                "char",
                "int",
                "float",
                "string"
            ],
            correct_option=0,
            explanation="char stores a single character such as 'A'."
        ),
    ])

    db.add(quiz)
    await db.commit()
    print("✅ Part 1 Concepts seeded successfully.")


async def seed_part2_concepts(db):
    quiz = Quiz(
        title="C Programming - Part 2 Concepts",
        description="Constants, Keywords, Identifiers, Operators, printf(), scanf(), if/else, switch, Loops",
        difficulty=DifficultyLevel.easy,
        subject="Programming",
        topic="C Programming Basics",
        quiz_type=QuizType.live.value,
        is_active=True,
    )

    quiz.questions.extend([
        Question(
            text="What is a constant in C?",
            options=[
                "A variable whose value changes frequently",
                "A value that cannot be changed during program execution",
                "A function",
                "A loop"
            ],
            correct_option=1,
            explanation="Constants remain unchanged throughout program execution."
        ),
        Question(
            text="Which of the following is the best example of a constant?",
            options=[
                "Student age",
                "Bank balance",
                "Number of days in a week",
                "Current temperature"
            ],
            correct_option=2,
            explanation="The number of days in a week is always 7."
        ),
        Question(
            text="What are keywords in C?",
            options=[
                "Names chosen by programmers",
                "Reserved words with predefined meanings",
                "Comments",
                "Header files"
            ],
            correct_option=1,
            explanation="Keywords are reserved by the C language and cannot be used as identifiers."
        ),
        Question(
            text="Which of the following is NOT a C keyword?",
            options=[
                "while",
                "return",
                "printf",
                "switch"
            ],
            correct_option=2,
            explanation="printf() is a library function, not a keyword."
        ),
        Question(
            text="An identifier is",
            options=[
                "A reserved keyword",
                "A programmer-defined name",
                "A compiler",
                "A loop"
            ],
            correct_option=1,
            explanation="Identifiers are names given to variables, functions, arrays, etc."
        ),
        Question(
            text="Which is a valid identifier?",
            options=[
                "2marks",
                "student_marks",
                "float",
                "while"
            ],
            correct_option=1,
            explanation="Identifiers cannot start with numbers or use reserved keywords."
        ),
        Question(
            text="Which operator is used to assign a value to a variable?",
            options=[
                "==",
                "=",
                "!=",
                ">"
            ],
            correct_option=1,
            explanation="The assignment operator '=' stores a value in a variable."
        ),
        Question(
            text="Which operator checks whether two values are equal?",
            options=[
                "=",
                "==",
                "!=",
                "+="
            ],
            correct_option=1,
            explanation="'==' compares two values for equality."
        ),
        Question(
            text="Which operator returns true only if both conditions are true?",
            options=[
                "||",
                "&&",
                "!",
                "%"
            ],
            correct_option=1,
            explanation="Logical AND (&&) requires both expressions to be true."
        ),
        Question(
            text="What is the purpose of printf()?",
            options=[
                "Accept input",
                "Display output",
                "Declare variables",
                "Create loops"
            ],
            correct_option=1,
            explanation="printf() displays formatted output on the screen."
        ),
        Question(
            text="What is the purpose of scanf()?",
            options=[
                "Display output",
                "Read input from the user",
                "Create variables",
                "Compile the program"
            ],
            correct_option=1,
            explanation="scanf() accepts input from the keyboard."
        ),
        Question(
            text="Which statement is mainly used to make decisions in a program?",
            options=[
                "for",
                "if-else",
                "printf",
                "continue"
            ],
            correct_option=1,
            explanation="if-else allows programs to choose between different paths."
        ),
        Question(
            text="Which statement is best suited for selecting one option from multiple fixed choices?",
            options=[
                "while",
                "switch",
                "if",
                "for"
            ],
            correct_option=1,
            explanation="switch is ideal for menu-driven programs."
        ),
        Question(
            text="Which loop is preferred when the number of iterations is already known?",
            options=[
                "while",
                "do-while",
                "for",
                "switch"
            ],
            correct_option=2,
            explanation="for loops are commonly used when the number of repetitions is known."
        ),
        Question(
            text="Which loop always executes its body at least once?",
            options=[
                "for",
                "while",
                "do-while",
                "switch"
            ],
            correct_option=2,
            explanation="The condition in a do-while loop is checked after executing the loop body."
        ),
    ])

    db.add(quiz)
    await db.commit()
    print("✅ Part 2 Concepts seeded successfully.")


async def seed_part1_logic(db):
    quiz = Quiz(
        title="C Programming - Part 1 Logic",
        description="Program Output and Basic Logic",
        difficulty=DifficultyLevel.easy,
        subject="Programming",
        topic="Introduction to C",
        quiz_type=QuizType.live.value,
        is_active=True,
    )

    quiz.questions.extend([
        Question(
            text="What is the output?\n\nprintf(\"Hello World\");",
            options=[
                "Hello World",
                "\"Hello World\"",
                "Error",
                "Nothing"
            ],
            correct_option=0,
            explanation="printf() prints the given string."
        ),
        Question(
            text="What is the output?\n\nint age=20;\nprintf(\"%d\",age);",
            options=[
                "20",
                "age",
                "%d",
                "Error"
            ],
            correct_option=0,
            explanation="age stores 20."
        ),
        Question(
            text="What is the output?\n\nint a=5;\nprintf(\"%d\",a+2);",
            options=[
                "5",
                "7",
                "2",
                "Error"
            ],
            correct_option=1,
            explanation="5+2 = 7."
        ),
        Question(
            text="What is the output?\n\nint a=10,b=20;\nprintf(\"%d\",a+b);",
            options=[
                "10",
                "20",
                "30",
                "200"
            ],
            correct_option=2,
            explanation="10+20=30."
        ),
        Question(
            text="What is the output?\n\nchar ch='A';\nprintf(\"%c\",ch);",
            options=[
                "65",
                "A",
                "a",
                "Error"
            ],
            correct_option=1,
            explanation="%c prints a character."
        ),
        Question(
            text="What is the output?\n\nchar ch='A';\nprintf(\"%d\",ch);",
            options=[
                "A",
                "97",
                "65",
                "Error"
            ],
            correct_option=2,
            explanation="ASCII value of A is 65."
        ),
        Question(
            text="What is the output?\n\nfloat x=3.5;\nprintf(\"%.1f\",x);",
            options=[
                "3",
                "3.5",
                "4",
                "Error"
            ],
            correct_option=1,
            explanation="Displays one decimal place."
        ),
        Question(
            text="What is the output?\n\nprintf(\"%d\",10+20*3);",
            options=[
                "90",
                "60",
                "70",
                "30"
            ],
            correct_option=2,
            explanation="Multiplication has higher precedence."
        ),
        Question(
            text="What is the output?\n\nprintf(\"%d\",(10+20)*3);",
            options=[
                "90",
                "70",
                "60",
                "30"
            ],
            correct_option=0,
            explanation="Parentheses execute first."
        ),
        Question(
            text="What is the output?\n\nprintf(\"%d\",15/2);",
            options=[
                "7",
                "7.5",
                "8",
                "15"
            ],
            correct_option=0,
            explanation="Integer division removes the decimal part."
        ),
        Question(
            text="What is the output?\n\nprintf(\"%.2f\",15.0/2);",
            options=[
                "7",
                "7.50",
                "8",
                "15"
            ],
            correct_option=1,
            explanation="Floating-point division gives 7.50."
        ),
        Question(
            text="What is the output?\n\nint x=5;\nprintf(\"%d\",x*x);",
            options=[
                "10",
                "25",
                "55",
                "5"
            ],
            correct_option=1,
            explanation="5 × 5 = 25."
        ),
        Question(
            text="Which header file is required for printf()?",
            options=[
                "math.h",
                "stdio.h",
                "string.h",
                "stdlib.h"
            ],
            correct_option=1,
            explanation="printf() is declared in stdio.h."
        ),
        Question(
            text="Which function starts execution of every C program?",
            options=[
                "printf()",
                "start()",
                "main()",
                "scanf()"
            ],
            correct_option=2,
            explanation="Execution begins from main()."
        ),
        Question(
            text="What is the output?\n\nint a=2;\nint b=3;\nprintf(\"%d\",a*b+a);",
            options=[
                "8",
                "10",
                "6",
                "5"
            ],
            correct_option=0,
            explanation="2×3+2 = 8."
        ),
    ])

    db.add(quiz)
    await db.commit()
    print("✅ Part 1 Logic seeded successfully.")


async def seed_part2_logic(db):
    quiz = Quiz(
        title="C Programming - Part 2 Logic",
        description="Operators, Decision Making and Loops",
        difficulty=DifficultyLevel.medium,
        subject="Programming",
        topic="C Programming Logic",
        quiz_type=QuizType.live.value,
        is_active=True,
    )

    quiz.questions.extend([
        Question(
            text="What is the output?\n\nint x=5;\nprintf(\"%d\",x++);",
            options=["5", "6", "Error", "Undefined"],
            correct_option=0,
            explanation="Post-increment returns the current value, then increments."
        ),
        Question(
            text="What is the output?\n\nint x=5;\nprintf(\"%d\",++x);",
            options=["5", "6", "Error", "Undefined"],
            correct_option=1,
            explanation="Pre-increment increments first, then prints."
        ),
        Question(
            text="What is the output?\n\nprintf(\"%d\",10%3);",
            options=["0", "1", "3", "10"],
            correct_option=1,
            explanation="10 divided by 3 leaves remainder 1."
        ),
        Question(
            text="What is the output?\n\nif(5>3)\nprintf(\"Yes\");\nelse\nprintf(\"No\");",
            options=["Yes", "No", "Error", "Nothing"],
            correct_option=0,
            explanation="5 is greater than 3."
        ),
        Question(
            text="What is the output?\n\nint a=0;\nif(a)\nprintf(\"True\");\nelse\nprintf(\"False\");",
            options=["True", "False", "0", "Error"],
            correct_option=1,
            explanation="0 is treated as false."
        ),
        Question(
            text="What is the output?\n\nint a=5;\nif(a)\nprintf(\"True\");",
            options=["True", "False", "Error", "Nothing"],
            correct_option=0,
            explanation="Any non-zero value is treated as true."
        ),
        Question(
            text="What is the output?\n\nswitch(2)\n{\ncase 1: printf(\"One\"); break;\ncase 2: printf(\"Two\"); break;\ndefault: printf(\"Other\");\n}",
            options=["One", "Two", "Other", "Error"],
            correct_option=1,
            explanation="Case 2 matches."
        ),
        Question(
            text="What is the output?\n\nswitch(2)\n{\ncase 1: printf(\"One\");\ncase 2: printf(\"Two\");\ncase 3: printf(\"Three\");\n}",
            options=[
                "One",
                "Two",
                "TwoThree",
                "Error"
            ],
            correct_option=2,
            explanation="Without break, execution falls through."
        ),
        Question(
            text="What is the output?\n\nfor(int i=1;i<=3;i++)\nprintf(\"%d\",i);",
            options=[
                "123",
                "012",
                "321",
                "Error"
            ],
            correct_option=0,
            explanation="Loop prints 1,2,3."
        ),
        Question(
            text="What is the output?\n\nint i=3;\nwhile(i>0)\n{\nprintf(\"%d\",i);\ni--;\n}",
            options=[
                "123",
                "321",
                "012",
                "Error"
            ],
            correct_option=1,
            explanation="Countdown from 3."
        ),
        Question(
            text="What is the output?\n\nint i=5;\ndo\n{\nprintf(\"%d\",i);\n}\nwhile(i<5);",
            options=[
                "5",
                "Nothing",
                "Error",
                "55"
            ],
            correct_option=0,
            explanation="do-while executes at least once."
        ),
        Question(
            text="What is the output?\n\nprintf(\"%d\",5>3 && 10>2);",
            options=[
                "0",
                "1",
                "True",
                "Error"
            ],
            correct_option=1,
            explanation="Both conditions are true."
        ),
        Question(
            text="What is the output?\n\nprintf(\"%d\",5<3 || 10>2);",
            options=[
                "0",
                "1",
                "True",
                "Error"
            ],
            correct_option=1,
            explanation="One condition is true."
        ),
        Question(
            text="Which operator is used for comparison?",
            options=[
                "=",
                "==",
                "+=",
                ":="
            ],
            correct_option=1,
            explanation="'==' compares two values."
        ),
        Question(
            text="What is the output?\n\nint x=2;\nint y=3;\nprintf(\"%d\",x<y);",
            options=[
                "0",
                "1",
                "2",
                "3"
            ],
            correct_option=1,
            explanation="2 is less than 3, so the expression evaluates to true (1)."
        ),
    ])

    db.add(quiz)
    await db.commit()
    print("✅ Part 2 Logic seeded successfully.")


async def seed():
    await init_db()

    async with AsyncSessionLocal() as db:
        try:
            await seed_part1_concepts(db)
            await seed_part2_concepts(db)
            await seed_part1_logic(db)
            await seed_part2_logic(db)
            print("🚀 Seed process completed successfully!")
        except Exception as e:
            await db.rollback()
            print(f"❌ Error during seeding: {e}")
            raise


if __name__ == "__main__":
    asyncio.run(seed())