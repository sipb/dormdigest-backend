"""
NOTE: Before running, first initialize model with `python3 ntlk_setup.py`

This module performs:
- Replace domains with "domain.com" or "DOMAIN.COM", while keeping subdomains the same
- Replace email **usernames** with "username"
- Replace **names** with "Firstname Lastname"
- Replace IP addresses with "127.0.0.1"

TODO: Add support for removing links (even in quoted-printable format)
TODO: Add support for sanitizing base64-encoded content in email
"""
import re
from nltk import ne_chunk, pos_tag, word_tokenize
from nltk.tree import Tree

#Ingest folder path (for original, unmodified emails)
FOLDER_PATH = "./src/test_emails/"


def main():
   # Example usage
   sanitizer = EmailSanitizer(FOLDER_PATH+"senior-sale-update.txt")  
   sanitizer.initialize() # Read in file text
   sanitizer.sanitize()   # Perform necessary sanitization
   print(sanitizer.get_text()[:5000]) # Retrieve the sanitized text

class EmailSanitizer:

   def __init__(self, filename):
      self.filename = filename

   def initialize(self):
      # Read in file
      with open(self.filename,"rt") as f:
         self.email = f.read()
                  
   def sanitize(self):
      self.remove_email_username()
      self.remove_ip_address()
      self.obfuscate_domain()
      self.remove_names()
      #self.remove_links()

   def get_text(self):
      return self.email
   
   def remove_email_username(self):
      EMAIL_RE = r"(([a-zA-Z0-9_+]+(?:\.[\w-]+)*)@((?:[\w-]+\.)*\w[\w-]{0,66})\.([a-z]{2,6}(?:\.[a-z]{2})?))"
      self.email = re.sub(EMAIL_RE, r"username@\3.\4", self.email)
   
   def remove_ip_address(self):
      # https://stackoverflow.com/questions/827557/how-do-you-validate-a-url-with-a-regular-expression-in-python
      IPV4_RE = r'(?:0|25[0-5]|2[0-4]\d|1\d?\d?|[1-9]\d?)(?:\.(?:0|25[0-5]|2[0-4]\d|1\d?\d?|[1-9]\d?)){3}'
      IPV6_RE = r'\[?((([0-9A-Fa-f]{1,4}:){7}([0-9A-Fa-f]{1,4}|:))|(([0-9A-Fa-f]{1,4}:){6}(:[0-9A-Fa-f]{1,'\
                  r'4}|((25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)(\.(25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)){3})|:))|(([0-9A-Fa-f]{'\
                  r'1,4}:){5}(((:[0-9A-Fa-f]{1,4}){1,2})|:((25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)(\.(25[0-5]|2['\
                  r'0-4]\d|1\d\d|[1-9]?\d)){3})|:))|(([0-9A-Fa-f]{1,4}:){4}(((:[0-9A-Fa-f]{1,4}){1,'\
                  r'3})|((:[0-9A-Fa-f]{1,4})?:((25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)(\.(25[0-5]|2[0-4]\d|1\d\d|['\
                  r'1-9]?\d)){3}))|:))|(([0-9A-Fa-f]{1,4}:){3}(((:[0-9A-Fa-f]{1,4}){1,4})|((:[0-9A-Fa-f]{1,4}){0,'\
                  r'2}:((25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)(\.(25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)){3}))|:))|((['\
                  r'0-9A-Fa-f]{1,4}:){2}(((:[0-9A-Fa-f]{1,4}){1,5})|((:[0-9A-Fa-f]{1,4}){0,3}:((25[0-5]|2['\
                  r'0-4]\d|1\d\d|[1-9]?\d)(\.(25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)){3}))|:))|(([0-9A-Fa-f]{1,4}:){1}(((:['\
                  r'0-9A-Fa-f]{1,4}){1,6})|((:[0-9A-Fa-f]{1,4}){0,4}:((25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)(\.(25[0-5]|2['\
                  r'0-4]\d|1\d\d|[1-9]?\d)){3}))|:))|(:(((:[0-9A-Fa-f]{1,4}){1,7})|((:[0-9A-Fa-f]{1,4}){0,'\
                  r'5}:((25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)(\.(25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)){3}))|:)))(%.+)?\]?'
      URL_RE = r'('+IPV4_RE + '|' + IPV6_RE+')'
      self.email = re.sub(URL_RE, "127.0.0.1", self.email)

   def obfuscate_domain(self):
      self.email = re.sub(r"([a-z0-9|-]+\.)*[a-z0-9|-]+\.[a-z]+", r"\1domain.com", self.email)  # Lowercase
      self.email = re.sub(r"([A-Z0-9|-]+\.)*[A-Z0-9|-]+\.[A-Z]+", r"\1DOMAIN.COM", self.email)  # Uppercase
      
   def remove_names(self):
      # Code reference from <https://unbiased-coder.com/extract-names-python-nltk/>
      
      # Define some common mislabeled names by NTLK in emails to be ignored
      EXCLUDE_NAMES = {'Segoe WP', 'Calibri', 'Helvetica', 'Segoe WP Light', 'Segoe UI', 'Segoe UI Light', 
                       'Gothic', 'Cambria Math', 'Microsoft Word', 'Style Definitions', 'Font Definitions',
                       'Symbol', 'Microsoft SMTP Server', 'Subject', 'Frontend Transport', 'Sale', 'Clothes'}
      found_names = set()
      nltk_results = ne_chunk(pos_tag(word_tokenize(self.email)))
      for nltk_result in nltk_results:
         if type(nltk_result) == Tree:
            name = ''
            for nltk_result_leaf in nltk_result.leaves():
                  name += nltk_result_leaf[0] + ' '
            name = name.rstrip()
            if nltk_result.label() == "PERSON" and name not in EXCLUDE_NAMES:
               found_names.add(name)
      print("Found names:",found_names)
      
      # Could be optimized with re.sub() but our emails aren't that large anyways
      # TODO: Make this more performant
      for name in found_names:
         if len(name.split(" ")) == 1: # Firstname
            self.email = self.email.replace(name,"Firstname")
         else:                         # Firstname Lastname (or some longer name)
            self.email = self.email.replace(name, "Firstname Lastname")
   
   def remove_links(self):
      ## NOTE: EXPERIMENTAL. Is only able to get the beginning of URLS
      ## but unable to properly extract everything due to whitespace
      ## TODO: Consider how to replace links while maintaining quotable printable format
      URL_RE = r"(?i)\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:'\".,<>?«»“”‘’]))"
      self.email = re.findall(URL_RE, self.email)

if __name__ == "__main__":
   main()