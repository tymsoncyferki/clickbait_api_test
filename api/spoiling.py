from openai import OpenAI
import json

from config import Config, logger

def get_spoiling_api_response(title, article_text, model="gpt-4o-mini"):
    client = OpenAI(api_key=Config.OPENAI_API_KEY)
    
    system_prompt = f"""\
        You are a model designed to generate concise, short spoilers from articles as "spoiler".\
        Your task is to analyze the main question or topic posed by the article's title ("title") and generate a spoiler based on the content provided in the article's paragraphs ("article_text"). Your response must include a JSON object with the key "spoiler".\
        Guidelines:\
        1. Use "title" to determine the central question or topic the spoiler should address.\
        2. Review "article_text" to find the most relevant details that directly answer the question or topic posed in the title.\
        Example Answer: {{\
            "spoiler": "<A short, concise model-generated spoiler>"\
        }}\
        Example 1:\
        Input{{\
            "title": "Wes Welker Wanted Dinner With Tom Brady, But Patriots QB Had A Better Idea"\
            "article_text": "It will be just like old times this weekend for Tom Brady and Wes Welker. Welker revealed Friday morning on a Miami radio station that he contacted Brady because he will be in town for Sunday’s game between the New England Patriots and Miami Dolphins at Gillette Stadium. It seemed like a perfect opportunity for the two to catch up. But Brady’s definition of catching up involves far more than just a meal. In fact, it involves some literal catching as the Patriots quarterback looks to stay sharp during his four-game Deflategate suspension. I hit him up to do dinner Saturday night. He is like, ‘I am going to be flying in from Ann Arbor later (after the Michigan-Colorado football game) but how about that morning we go throw?  Welker said on WQAM, per The Boston Globe. And I am just sitting there, I am like, ‘I was just thinking about dinner, but yeah, sure. I will get over there early and we can throw a little bit. , Welker was one of Brady’s favorite targets for six seasons from 2007 to 2012. It is understandable him and Brady want to meet with both being in the same area. But Brady typically is all business during football season. Welker probably should have known what he was getting into when reaching out to his buddy. That is the only thing we really have planned, Welker said of his upcoming workout with Brady. It is just funny. I am sitting there trying to have dinner. ‘Hey, get your ass up here and let us go throw. I am like, ‘Aw jeez, man. He is going to have me running like 2-minute drills in his backyard or something. Maybe Brady will put a good word in for Welker down in Foxboro if the former Patriots wide receiver impresses him enough."
        }}\
        \
        Output{{\
            "spoiler": 'They threw a ball'\
        }}\
        \
        Example 2:\
        Input{{\
            "title": 'The Reason Why Gabor Kiraly Wears THOSE Trackie Bottoms',\
            "article_text": 'June 14th 2016 3.3K Shares, They may look like the sort of apparel you would usually sport on the morning after 12 pints, just so the elasticated waist can provide enough give to support two hangover curing trips to Maccy Ds and an evening Dominos, just for good measure, but Gabor Kiraly has made a name for himself by wearing grey tracksuit bottoms, as a professional footballer, for the last 16 years. But, why? Why would you favour a pair of pants that look like they might have been found in the lost property bin of a secondary school? Are they fused to him? Are his legs allergic to grass? Is he constantly hungover? In fact, the reason the oldest player at Euro 2016 wears those snazzy, grey marl bastards is down to a longstanding superstition or kabbalah, as he explained during an interview, in 2005: The more good games I had in them, the more I got used to them. I had many good games in them, especially at Hertha Berlin in the Champions League and with the Hungarian national team. Hell be hoping they provide Hungary with plenty of luck during the European Championships.'\
        }}\
        Output{{\
            "spoiler": 'Its a lucky charm to him'\
        }}\
        The response should be as short as possible, more of a phrase rather than sophisticated sentence.
        However, it should not be just a rephrase of the title or a summary whats the text about.
        It should satisfy the curiosity created by the clickbait title and create a 'spoiler' of the content.
        Pay attention to return valid JSON format!\
        """

    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system_prompt},
                {
                    "role": "user",
                    "content": f"{{title: '{title}', article_text: {article_text}}}"
                }
            ]
        )
        prediction_json = json.loads(response.choices[0].message.content)
        return prediction_json
    except Exception as e:
        logger.error(f"There was a problem fetching response from OpenAI API: {e}, setting spoiler to empty string")
        return {"spoiler": ""}    
    

def get_spoiler(title, article_text):
    response = get_spoiling_api_response(title, article_text)
    try:
        spoiler = response['spoiler']
    except Exception as e:
        logger.error(f"Could not extract spoiler from the response: {e}, setting spoiler to empty string")
        spoiler = ""
    return spoiler
    
