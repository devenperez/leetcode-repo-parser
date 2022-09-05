"""
This code is based off JavaScript code from LeetHub by Qasim Wani
The original code can be found on GitHub (https://github.com/QasimWani/LeetHub)
"""
import io
from time import sleep
import urllib.request
import webbrowser
from selenium import webdriver

# Parser function for the question and tags 
def parseQuestion(url, htmlFile):
    questionUrl = str(url)
    if (questionUrl.endswith('/submissions/')):
        questionUrl = questionUrl[0:questionUrl.index('/submissions/') + 1]
        
    questionElem = getElemByClassName('content__u3I1 question-content__JfgR')
    questionDescriptionElem = getElemByClassName('question-description__3U1T')

    if (checkElem(questionElem)):
        qbody = questionElem[0].innerHTML

        # Problem title.
        qtitle = getElemByClassName('css-v3d350')
        if (checkElem(qtitle)):
            qtitle = qtitle[0].innerHTML
        else:
            qtitle = 'unknown-problem'
        

        # Problem difficulty, each problem difficulty has its own class.
        isHard = getElemByClassName('css-t42afm')
        isMedium = getElemByClassName('css-dcmtd5')
        isEasy = getElemByClassName('css-14oi08n')

        if (checkElem(isEasy)):
            difficulty = 'Easy'
        elif (checkElem(isMedium)):
            difficulty = 'Medium'
        elif (checkElem(isHard)):
            difficulty = 'Hard'
        
        # Final formatting of the contents of the README for each problem
        markdown = f"<h2><a href=\"{questionUrl}\">{qtitle}</a></h2><h3>{difficulty}</h3><hr>{qbody}"
        return markdown
    elif (checkElem(questionDescriptionElem)):
        questionTitle = getElemByClassName('question-title')
        if (checkElem(questionTitle)):
            questionTitle = questionTitle[0].innerText
        else:
            questionTitle = 'unknown-problem'
        

        questionBody = questionDescriptionElem[0].innerHTML
        markdown = f"<h2>{questionTitle}</h2><hr>{questionBody}"

        return markdown

    return None

# Util function to check if an element exists
def checkElem(elem):
    return elem and len(elem) > 0

"""
Things that I need to add for this to work:
- getting tags from class names (doesn't really need to return multiple, the one is fine as long as I remove references to arrays)
- innerHTML() for those tags
- proper HTML searching to find these tags
"""
# Helper functions to survive the environment changes
def getElemByClassName(className, htmlURL):
    # hdrs = {
    #     "User-Agent":"Mozilla/5.0",
    #     "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"
    #     }
    # req = urllib.request.Request(htmlURL, headers=hdrs)
    # file = urllib.request.urlopen(req)


    # for l in file:
    #     decoded = l.decode("utf-8")
    #     print(decoded)

    print("1")
    chrome = webdriver.Chrome("C:\Program Files\ChromeDriver\chromedriver.exe")
    chrome.get(htmlURL)
    print("2")
    sleep(5)
    print(f"app resp: {chrome.find_element(value='app')}")
    chrome.find_element(value='app')
    print("3")
    hope = chrome.execute_script("""
    /* Util function to check if an element exists */
    function checkElem(elem) {
    return elem && elem.length > 0;
    }

    /* Parser function for the question and tags */
    function parseQuestion() {
    var questionUrl = window.location.href;
    if (questionUrl.endsWith('/submissions/')) {
        questionUrl = questionUrl.substring(
        0,
        questionUrl.lastIndexOf('/submissions/') + 1,
        );
    }
    const questionElem = document.getElementsByClassName(
        'content__u3I1 question-content__JfgR',
    );
    const questionDescriptionElem = document.getElementsByClassName(
        'question-description__3U1T',
    );
    if (checkElem(questionElem)) {
        const qbody = questionElem[0].innerHTML;

        // Problem title.
        let qtitle = document.getElementsByClassName('css-v3d350');
        if (checkElem(qtitle)) {
        qtitle = qtitle[0].innerHTML;
        } else {
        qtitle = 'unknown-problem';
        }

        // Problem difficulty, each problem difficulty has its own class.
        const isHard = document.getElementsByClassName('css-t42afm');
        const isMedium = document.getElementsByClassName('css-dcmtd5');
        const isEasy = document.getElementsByClassName('css-14oi08n');

        if (checkElem(isEasy)) {
        difficulty = 'Easy';
        } else if (checkElem(isMedium)) {
        difficulty = 'Medium';
        } else if (checkElem(isHard)) {
        difficulty = 'Hard';
        }
        // Final formatting of the contents of the README for each problem
        const markdown = `<h2><a href="${questionUrl}">${qtitle}</a></h2><h3>${difficulty}</h3><hr>${qbody}`;
        return markdown;
    } else if (checkElem(questionDescriptionElem)) {
        let questionTitle = document.getElementsByClassName(
        'question-title',
        );
        if (checkElem(questionTitle)) {
        questionTitle = questionTitle[0].innerText;
        } else {
        questionTitle = 'unknown-problem';
        }

        const questionBody = questionDescriptionElem[0].innerHTML;
        const markdown = `<h2>${questionTitle}</h2><hr>${questionBody}`;

        return markdown;
    }

    return "null";
    }

    parseQuestion()
    """)
    print("4")
    print(f"hope={hope}")
    chrome.close()

class Tag:
    def __init__(self) -> None:
        self.tag = ""
        self.classes = []
        self.innerHTML = ""


getElemByClassName("", "https://leetcode.com/problems/two-sum/")
