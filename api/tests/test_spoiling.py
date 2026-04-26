from spoiling import get_spoiling_api_response
import unittest

class TestSpoiling(unittest.TestCase):

    def test_spoiler_generation(self):
        title = "Intellectual Stimulation Trumps Money For Employee Happiness, Survey Finds"
        article_text = "Despite common belief, money is not the key to employee happiness, new research finds. A study by hiring software provider Cangrade revealed that being intellectually stimulated is the most important aspect of an employees job satisfaction. Specially, those surveyed said intellectual stimulation accounts for 18.5 percent of their job satisfaction. That Is compared to money, which accounts for just 5.4 percent of how happy an employee is with the job. Achievement and prestige, power and influence, work-life balance and affiliation and friendship were all rated more important to job satisfaction than money. These findings are quite surprising, because employers often assume things like income are the strongest drivers of happiness in the workplace, said Steve Lehr, Cangrade\\s chief science officer. In fact, our research shows that it may be the weakest. Researchers developed a three-part formula for employers who are eager to keep their staff happy: Try to ensure that jobs provide intellectual stimulation and task variety. Give employees some autonomy, influence and opportunities to acquire prestige and recognition. Employers should give employees these things even when they do not say they need them. Give them even more if they say they do. Employers should give all employees a break now and again, including the consummate workaholics who say they do not want or need it. Offer employees extra money, security and social opportunities. However, only to the extent they say these things matter to them. If there is a major takeaway here, it\\s that we can finally prove that money doesn\\t buy happiness, and that happiness isn\\t as elusive as we might think, said Cangrade CEO Michael Burtov. The study was based on surveys of nearly 600 YOU.S. employees."
        res = get_spoiling_api_response(title, article_text)
        spoiler = res['spoiler']
        self.assertGreater(len(spoiler), 10)

if __name__ == "__main__":
    unittest.main()