import jinja2

templ_env = jinja2.Environment(loader=jinja2.FileSystemLoader('./templates'))

def render(filename, **kwargs):
    return templ_env.get_template(filename).render(**kwargs)

class Tester:
    def __init__(self, test_content):
        self.test_content = test_content

    def echo_0(self):
        return self.test_content

    def echo_1(self, additional_content):
        return self.test_content + additional_content

def main():
    print render('index.html', t=Tester('Hello'))

if __name__ == '__main__': main()
