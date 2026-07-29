"""
Create sample users.

Usage:
    python seed_user.py
"""

import asyncio

from sqlalchemy import select

from app.database import AsyncSessionLocal, init_db
from app.models.user import User
from app.core.security import hash_password


SAMPLE_USERS =[
  {
    "name": "Suganthan A K V",
    "username": "suganthanakv28042006",
    "email": "suganthanakv@gmail.com",
    "password": "suganthanakv@123",
    "is_admin": False,
    "profile_url": None
  },
  {
    "name": "Sai pranesh",
    "username": "saipranesh05062006",
    "email": "Saipranesh44@gmail.com",
    "password": "saipranesh@123",
    "is_admin": False,
    "profile_url": None
  },
  {
    "name": "Aaghash M",
    "username": "aaghashm27012007",
    "email": "aaghashsarvesh@gmail.com",
    "password": "aaghashm@123",
    "is_admin": False,
    "profile_url": None
  },
  {
    "name": "Sanjay K",
    "username": "sanjayk14082006",
    "email": "sanjayk140820006@gmail.com",
    "password": "sanjayk@123",
    "is_admin": False,
    "profile_url": None
  },
  {
    "name": "Shree hari JS",
    "username": "shreeharijs15112006",
    "email": "Shreehari.24me@kct.ac.in",
    "password": "shreeharijs@123",
    "is_admin": False,
    "profile_url": None
  },
  {
    "name": "Gokul S",
    "username": "gokuls29012006",
    "email": "gokul.24ee@kct.ac.in",
    "password": "gokuls@123",
    "is_admin": False,
    "profile_url": None
  },
  {
    "name": "Nirmal M",
    "username": "nirmalm31052007",
    "email": "nirmal.24au@kct.ac.in",
    "password": "nirmalm@123",
    "is_admin": False,
    "profile_url": None
  },
  {
    "name": "Keerthana Priya P",
    "username": "keerthanapriyap31102006",
    "email": "keerthanapriya.24ce@kct.ac.in",
    "password": "keerthanapriyap@123",
    "is_admin": False,
    "profile_url": None
  },
  {
    "name": "Yazhini.G",
    "username": "yazhinig26032026",
    "email": "Yazhini.24au@kct.ac.in",
    "password": "yazhinig@123",
    "is_admin": False,
    "profile_url": None
  },
  {
    "name": "Tharrun",
    "username": "tharrun16122006",
    "email": "tharrunnus@gmail.com",
    "password": "tharrun@123",
    "is_admin": False,
    "profile_url": None
  },
  {
    "name": "Akeel Rahman.S.N",
    "username": "akeelrahmansn18062006",
    "email": "akeelrahman.24me@kct.ac.in",
    "password": "akeelrahmansn@123",
    "is_admin": False,
    "profile_url": None
  },
  {
    "name": "Sudharsan N",
    "username": "sudharsann23092006",
    "email": "sudharsan.24ee@kct.ac.in",
    "password": "sudharsann@123",
    "is_admin": False,
    "profile_url": None
  },
  {
    "name": "Sidarth S",
    "username": "sidarths10052006",
    "email": "sridharsidarth2006@gmail.com",
    "password": "sidarths@123",
    "is_admin": False,
    "profile_url": None
  },
  {
    "name": "Sanjay vignesh v",
    "username": "sanjayvigneshv01032006",
    "email": "sanjayvignesh.24me@kct.ac.in",
    "password": "sanjayvigneshv@123",
    "is_admin": False,
    "profile_url": None
  },
  {
    "name": "Simra akmal",
    "username": "simraakmal30082006",
    "email": "simraakmal.24ee@kct.ac.in",
    "password": "simraakmal@123",
    "is_admin": False,
    "profile_url": None
  },
  {
    "name": "Mugesh M",
    "username": "mugeshm06112006",
    "email": "mugesh0611@gmail.com",
    "password": "mugeshm@123",
    "is_admin": False,
    "profile_url": None
  },
  {
    "name": "Nithish Marshal.G",
    "username": "nithishmarshalg08062006",
    "email": "nithishmarshal.24ce@kct.ac.in",
    "password": "nithishmarshalg@123",
    "is_admin": False,
    "profile_url": None
  },
  {
    "name": "Harshanaa V",
    "username": "harshanaav21022005",
    "email": "harshanaa.24bt@kct.ac.in",
    "password": "harshanaav@123",
    "is_admin": False,
    "profile_url": None
  },
  {
    "name": "Deva sree R",
    "username": "devasreer01042007",
    "email": "devasree1407@gmail.com",
    "password": "devasreer@123",
    "is_admin": False,
    "profile_url": None
  },
  {
    "name": "Praveenkumar",
    "username": "praveenkumar12062006",
    "email": "praveenkumar.24tt@kct.ac.in",
    "password": "praveenkumar@123",
    "is_admin": False,
    "profile_url": None
  },
  {
    "name": "Jayarithanya A S",
    "username": "jayarithanyaas22122006",
    "email": "jayarithanyaas@gmail.com",
    "password": "jayarithanyaas@123",
    "is_admin": False,
    "profile_url": None
  },
  {
    "name": "Pradeep P",
    "username": "pradeepp03122005",
    "email": "pradeepgt16@gmail.com",
    "password": "pradeepp@123",
    "is_admin": False,
    "profile_url": None
  },
  {
    "name": "Hariharan k",
    "username": "hariharank26062004",
    "email": "hariharank2k04@gmail.com",
    "password": "hariharank@123",
    "is_admin": False,
    "profile_url": None
  },
  {
    "name": "Karthik S",
    "username": "karthiks30012007",
    "email": "karthiksnvsk9003privatelimited@gmail.com",
    "password": "karthiks@123",
    "is_admin": False,
    "profile_url": None
  },
  {
    "name": "VENKATESH K",
    "username": "venkateshk23102006",
    "email": "venkatesh.24ce@kct.ac.in",
    "password": "venkateshk@123",
    "is_admin": False,
    "profile_url": None
  },
  {
    "name": "Mukesh S",
    "username": "mukeshs05112007",
    "email": "mukesh.24me@kct.ac.in",
    "password": "mukeshs@123",
    "is_admin": False,
    "profile_url": None
  },
  {
    "name": "Akilan MP",
    "username": "akilanmp18102006",
    "email": "akillanmp64@gmail.com",
    "password": "akilanmp@123",
    "is_admin": False,
    "profile_url": None
  },
  {
    "name": "Muthukumaran pon",
    "username": "muthakumaranpon19122006",
    "email": "ridingspark.rosi46@gmail.com",
    "password": "muthakumaranpon@123",
    "is_admin": False,
    "profile_url": None
  },
  {
    "name": "Poovilzan S",
    "username": "poovilzans20072007",
    "email": "poovilzan56@gmail.com",
    "password": "poovilzans@123",
    "is_admin": False,
    "profile_url": None
  },
  {
    "name": "HARIKARAN S",
    "username": "harikarans17092006",
    "email": "harikaran.24ee@kct.ac.in",
    "password": "harikarans@123",
    "is_admin": False,
    "profile_url": None
  },
  {
    "name": "Vijaya Perumal S",
    "username": "vijayaperumals01102006",
    "email": "motom4637@gmail.com",
    "password": "vijayaperumals@123",
    "is_admin": False,
    "profile_url": None
  },
  {
    "name": "Nevathan V",
    "username": "nevathanv11052006",
    "email": "nevathan.24me@kct.ac.in",
    "password": "nevathanv@123",
    "is_admin": False,
    "profile_url": None
  },
  {
    "name": "Subash.K",
    "username": "subashk11062007",
    "email": "subashkrishnasamy7@gmail.com",
    "password": "subashk@123",
    "is_admin": False,
    "profile_url": None
  },
  {
    "name": "DIVAKAR",
    "username": "divakar07122007",
    "email": "divakar72007@gmail.com",
    "password": "divakar@123",
    "is_admin": False,
    "profile_url": None
  },
  {
    "name": "Mohammed Fadil A",
    "username": "mohammedfadila23062007",
    "email": "fadihr007@gmail.com",
    "password": "mohammedfadila@123",
    "is_admin": False,
    "profile_url": None
  },
  {
    "name": "A.Anumalya",
    "username": "aanumalya15122006",
    "email": "anmalayaanbazhagan@gmail.com",
    "password": "aanumalya@123",
    "is_admin": False,
    "profile_url": None
  },
  {
    "name": "Sugant",
    "username": "sugant25112006",
    "email": "sugant.24ee@kct.ac.in",
    "password": "sugant@123",
    "is_admin": False,
    "profile_url": None
  },
  {
    "name": "Pratheeswaran S",
    "username": "pratheeswarans15032006",
    "email": "Pratheeswaranwaran4@gmail.com",
    "password": "pratheeswarans@123",
    "is_admin": False,
    "profile_url": None
  },
  {
    "name": "S. Nandha",
    "username": "snandha10062006",
    "email": "nandhasaravanan10@gmail.com",
    "password": "snandha@123",
    "is_admin": False,
    "profile_url": None
  },
  {
    "name": "Vishnu Raju R",
    "username": "vishnurajur28072026",
    "email": "vishnurajur28072007@gmail.com",
    "password": "vishnurajur@123",
    "is_admin": False,
    "profile_url": None
  },
  {
    "name": "Muthukumaran",
    "username": "muthukumaran19122006",
    "email": "ridingspark.rosi46@gmail.com",
    "password": "muthukumaran@123",
    "is_admin": False,
    "profile_url": None
  },
  {
    "name": "Dimble",
    "username": "dimble09122006",
    "email": "dimble.24bt@kct.ac.in",
    "password": "dimble@123",
    "is_admin": False,
    "profile_url": None
  },
  {
    "name": "vishnuraju r",
    "username": "vishnurajur28072026",
    "email": "vishnurajur28072007@gmail.com",
    "password": "vishnurajur@123",
    "is_admin": False,
    "profile_url": None
  },
  {
    "name": "Nithin krishna K",
    "username": "nithinkrishnak09052007",
    "email": "nithinkrishna0709@gmail.com",
    "password": "nithinkrishnak@123",
    "is_admin": False,
    "profile_url": None
  },
  {
    "name": "Harish Kumar J",
    "username": "harishkumarj04052006",
    "email": "harishkumar.24me@kct.ac.in",
    "password": "harishkumarj@123",
    "is_admin": False,
    "profile_url": None
  },
  {
    "name": "Harshada",
    "username": "harshada27062006",
    "email": "harshadashanmugan@gmail.com",
    "password": "harshada@123",
    "is_admin": False,
    "profile_url": None
  },
  {
    "name": "Moheshwaran S",
    "username": "moheshwarans18102006",
    "email": "moheshwaran.24au@kct.ac.in",
    "password": "moheshwarans@123",
    "is_admin": False,
    "profile_url": None
  },
  {
    "name": "Sahana K",
    "username": "sahanak03112006",
    "email": "sahana.24au@kct.ac.in",
    "password": "sahanak@123",
    "is_admin": False,
    "profile_url": None
  },
  {
    "name": "Sri Vaishnavi S",
    "username": "srivaishnavis04102006",
    "email": "s.srivaishnavi2006@gmail.com",
    "password": "srivaishnavis@123",
    "is_admin": False,
    "profile_url": None
  },
  {
    "name": "KARTHIKEYAN M",
    "username": "karthikeyanm05092006",
    "email": "karthikeyan.24ft@kct.ac.in",
    "password": "karthikeyanm@123",
    "is_admin": False,
    "profile_url": None
  },
  {
    "name": "Dhaareni K",
    "username": "dhaarenik15072006",
    "email": "dhaarenikartick636012@gmail.com",
    "password": "dhaarenik@123",
    "is_admin": False,
    "profile_url": None
  },
  {
    "name": "Karthikeyan VR",
    "username": "karthikeyanvr02122006",
    "email": "karthikeyan.24ee@kct.ac.in",
    "password": "karthikeyanvr@123",
    "is_admin": False,
    "profile_url": None
  },
  {
    "name": "Shreyaa S",
    "username": "shreyaas03042007",
    "email": "shreyaa.24au@kct.ac.in",
    "password": "shreyaas@123",
    "is_admin": False,
    "profile_url": None
  },
  {
    "name": "Rejo Antony Nathan A",
    "username": "rejoantonynathana15092006",
    "email": "rejoantony.24ei@kct.ac.in",
    "password": "rejoantonynathana@123",
    "is_admin": False,
    "profile_url": None
  },
  {
    "name": "Annapoorni",
    "username": "annapoorni12092006",
    "email": "annapoorni.24bt@kct.ac.in",
    "password": "annapoorni@123",
    "is_admin": False,
    "profile_url": None
  },
  {
    "name": "Divya v",
    "username": "divyav13082007",
    "email": "divya.24ft@kct.ac.in",
    "password": "divyav@123",
    "is_admin": False,
    "profile_url": None
  },
  {
    "name": "Megala",
    "username": "megala09122006",
    "email": "megala.24bt@kct.ac.in",
    "password": "megala@123",
    "is_admin": False,
    "profile_url": None
  },
  {
    "name": "Pushpaniranjani",
    "username": "pushpaniranjani18122006",
    "email": "pushpaniranjani.24bt@kct.ac.in",
    "password": "pushpaniranjani@123",
    "is_admin": False,
    "profile_url": None
  },
  {
    "name": "GOPIKRISHNA",
    "username": "gopikrishna14102006",
    "email": "gopikrishna.24ei@kct.ac.in",
    "password": "gopikrishna@123",
    "is_admin": False,
    "profile_url": None
  },
  {
    "name": "Shanmugavel",
    "username": "shanmugavel22032007",
    "email": "shanmugavel.24tt@kct.ac.in",
    "password": "shanmugavel@123",
    "is_admin": False,
    "profile_url": None
  },
  {
    "name": "Prithi",
    "username": "prithi06112006",
    "email": "prithi.24ei@kct.ac.in",
    "password": "prithi@123",
    "is_admin": False,
    "profile_url": None
  },
  {
    "name": "ASWIN",
    "username": "aswin21032007",
    "email": "aswin.24ei@kct.ac.in",
    "password": "aswin@123",
    "is_admin": False,
    "profile_url": None
  },
  {
    "name": "Dhaareni",
    "username": "dhaareni15072006",
    "email": "dhaareni.24ee@kct.ac.in",
    "password": "dhaareni@123",
    "is_admin": False,
    "profile_url": None
  },
  {
    "name": "NithinkrishnaK",
    "username": "nithinkrishnak09052007",
    "email": "nithinkrishna.24ei@kct.ac.in",
    "password": "nithinkrishnak@123",
    "is_admin": False,
    "profile_url": None
  },
  {
    "name": "Moheshwaran",
    "username": "moheshwaran18102006",
    "email": "moheshwaran.24au@kct.ac.in",
    "password": "moheshwaran@123",
    "is_admin": False,
    "profile_url": None
  },
  {
    "name": "Karthikeyan",
    "username": "karthikeyan02122006",
    "email": "karthikeyan.24ee@kct.ac.in",
    "password": "karthikeyan@123",
    "is_admin": False,
    "profile_url": None
  },
  {
    "name": "LUKATONYAS",
    "username": "lukatonyas22062006",
    "email": "lukatony.24mc@kct.ac.in",
    "password": "lukatonyas@123",
    "is_admin": False,
    "profile_url": None
  },
  {
    "name": "Sahana",
    "username": "sahana03112006",
    "email": "sahana.24au@kct.ac.in",
    "password": "sahana@123",
    "is_admin": False,
    "profile_url": None
  },
  {
    "name": "Srivarsanjay M",
    "username": "srivarsanjaym20102006",
    "email": "srivarsanjay.24me@kct.ac.in",
    "password": "srivarsanjaym@123",
    "is_admin": False,
    "profile_url": None
  },
  {
    "name": "Joicevj",
    "username": "joicevj18102006",
    "email": "Joice.24me@kct.ac.in",
    "password": "joicevj@123",
    "is_admin": False,
    "profile_url": None
  },
  {
    "name": "Shreyaa",
    "username": "shreyaa03042007",
    "email": "shreyaa.24au@kct.ac.in",
    "password": "shreyaa@123",
    "is_admin": False,
    "profile_url": None
  },
  {
    "name": "HARIPRASANNA",
    "username": "hariprasanna18042007",
    "email": "223016a@gmail.com",
    "password": "hariprasanna@123",
    "is_admin": False,
    "profile_url": None
  },
  {
    "name": "ANAS",
    "username": "anas10102006",
    "email": "anas.24ei@kct.ac.in",
    "password": "anas@123",
    "is_admin": False,
    "profile_url": None
  },
  {
    "name": "MANIVASAGAM.B",
    "username": "manivasagamb13112006",
    "email": "manibalusamy06@gmail.com",
    "password": "manivasagamb@123",
    "is_admin": False,
    "profile_url": None
  },
  {
    "name": "Rejoantonynathan",
    "username": "rejoantonynathan15092006",
    "email": "rejoantony.24ei@kct.ac.in",
    "password": "rejoantonynathan@123",
    "is_admin": False,
    "profile_url": None
  },
  {
    "name": "MohamedAbubackerM",
    "username": "mohamedabubackerm10062006",
    "email": "mohamedabubacker.24me@kct.ac.in",
    "password": "mohamedabubackerm@123",
    "is_admin": False,
    "profile_url": None
  },
  {
    "name": "Saarves R",
    "username": "saarvesr17062006",
    "email": "saarves8@gmail.com",
    "password": "saarvesr@123",
    "is_admin": False,
    "profile_url": None
  },
  {
    "name": "YogeshKumar",
    "username": "yogeshkumar14022007",
    "email": "yogeshkumar.24mc@kct.ac.in",
    "password": "yogeshkumar@123",
    "is_admin": False,
    "profile_url": None
  },
  {
    "name": "DineshkarthickR",
    "username": "dineshkarthickr29112006",
    "email": "dineshkarthick.24me@kct.ac.in",
    "password": "dineshkarthickr@123",
    "is_admin": False,
    "profile_url": None
  },
  {
    "name": "SriVaishnavi",
    "username": "srivaishnavi04102006",
    "email": "srivaishnavi.24ee@kct.ac.in",
    "password": "srivaishnavi@123",
    "is_admin": False,
    "profile_url": None
  },
  {
    "name": "Aparnaa",
    "username": "aparnaa16052007",
    "email": "aparnaaa.24ft@kct.ac.in",
    "password": "aparnaa@123",
    "is_admin": False,
    "profile_url": None
  },
  {
    "name": "VishmithaVarsha",
    "username": "vishmithavarsha23082026",
    "email": "vishmithavarsha.24ft@kct.ac.in",
    "password": "vishmithavarsha@123",
    "is_admin": False,
    "profile_url": None
  },
  {
    "name": "Dhanalakshmi",
    "username": "dhanalakshmi07072007",
    "email": "dhanalakshmi.24ft@kct.ac.in",
    "password": "dhanalakshmi@123",
    "is_admin": False,
    "profile_url": None
  },
  {
    "name": "Parthasarathynambi",
    "username": "parthasarathynambi14072005",
    "email": "parthasarathynambi.24ee@kct.ac.in",
    "password": "parthasarathynambi@123",
    "is_admin": False,
    "profile_url": None
  },
  {
    "name": "Harshada",
    "username": "harshada27062006",
    "email": "harshada.24ee@kct.ac.in",
    "password": "harshada@123",
    "is_admin": False,
    "profile_url": None
  },
  {
    "name": "Harishkumarj",
    "username": "harishkumarj04052006",
    "email": "harishkumarj4506@gmail.com",
    "password": "harishkumarj@123",
    "is_admin": False,
    "profile_url": None
  },
  {
    "name": "MOHEMED ROSHAN T",
    "username": "mohemedroshant20122006",
    "email": "roshanmohamed484@gmail.com",
    "password": "mohemedroshant@123",
    "is_admin": False,
    "profile_url": None
  },
  {
    "name": "Akshaya",
    "username": "akshaya06012007",
    "email": "akshaya.24ft@kct.ac.in",
    "password": "akshaya@123",
    "is_admin": False,
    "profile_url": None
  },
  {
    "name": "Agileashpr",
    "username": "agileashpr26042006",
    "email": "agileash2006@gmail.com",
    "password": "agileashpr@123",
    "is_admin": False,
    "profile_url": None
  },
  {
    "name": "Karthikeyan",
    "username": "karthikeyan02122006",
    "email": "karthikeyan.24ee@kct.ac.in",
    "password": "karthikeyan@123",
    "is_admin": False,
    "profile_url": None
  },
  {
    "name": "ASWIN",
    "username": "aswin21032007",
    "email": "aswin.24ei@kct.ac.in",
    "password": "aswin@123",
    "is_admin": False,
    "profile_url": None
  },
  {
    "name": "lukatonyas",
    "username": "lukatonyas22062006",
    "email": "lukatony.24mc@kct.ac.in",
    "password": "lukatonyas@123",
    "is_admin": False,
    "profile_url": None
  },
  {
    "name": "harishkumar",
    "username": "harishkumar04052006",
    "email": "harishkumar.24me@kct.ac.in",
    "password": "harishkumar@123",
    "is_admin": False,
    "profile_url": None
  },
  {
    "name": "agileash",
    "username": "agileash26042006",
    "email": "agileash2006@gmail.com",
    "password": "agileash@123",
    "is_admin": False,
    "profile_url": None
  },
  {
    "name": "divyav",
    "username": "divyav13082007",
    "email": "divya.24ft@kct.ac.in",
    "password": "divyav@123",
    "is_admin": False,
    "profile_url": None
  },
  {
    "name": "karthikeyan",
    "username": "karthikeyan05092006",
    "email": "karthikeyan.24ft@kct.ac.in",
    "password": "karthikeyan@123",
    "is_admin": False,
    "profile_url": None
  },
  {
    "name": "Imthiyas ahamed I",
    "username": "imthiyasahamedic13072007",
    "email": "imthiyasahamed.24me@kct.ac.in",
    "password": "imthiyasahamedic@123",
    "is_admin": False,
    "profile_url": None
  },
  {
    "name": "Parthasarathynambi",
    "username": "parthasarathynambi14072005",
    "email": "Parthasarathynambi.24ee@kct.ac.in",
    "password": "parthasarathynambi@123",
    "is_admin": False,
    "profile_url": None
  }
]




async def seed_users():
    await init_db()

    async with AsyncSessionLocal() as db:
        try:
            for user_data in SAMPLE_USERS:
                result = await db.execute(
                    select(User).where(
                        (User.username == user_data["username"])
                        | (User.email == user_data["email"])
                    )
                )

                existing_user = result.scalar_one_or_none()

                if existing_user:
                    print(
                        f"⚠️ User already exists: {user_data['username']} ({user_data['email']})"
                    )
                    continue

                user = User(
                    name=user_data["name"],
                    username=user_data["username"],
                    email=user_data["email"],
                    hashed_password=hash_password(user_data["password"]),
                    is_admin=user_data["is_admin"],
                    profile_url=user_data["profile_url"],
                )

                db.add(user)
                print(f"➕ Added user: {user_data['username']}")

            await db.commit()
            print("✅ User seed completed!")

        except Exception as exc:
            await db.rollback()
            print(f"❌ User seed failed: {exc}")
            raise


if __name__ == "__main__":
    asyncio.run(seed_users())