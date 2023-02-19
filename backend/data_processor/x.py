from langchain.agents import load_tools
from langchain.agents import initialize_agent
from langchain.llms import OpenAI

#llm = OpenAI(temperature=0)

text = "What would be a good company name a company that makes colorful socks?"
#print(llm(text))


class X():
    a=1

def x(*args, **kwargs):
    print('args', args)
    print('kwargs', kwargs)

x(1,2,3, a=4)


"""
tools = load_tools(["serpapi", "llm-math"], llm=llm)
agent = initialize_agent(tools, llm, agent="zero-shot-react-description", verbose=True)
agent.run("What are the common adverse events in a hep A trial?")


class Hello():
    def __call__(self, msg):
        print('hello, ' + msg)

hello = Hello()
hello("there")

"""
