from googletrans import Translator

tar = Translator()
print((tar.translate('salom', src='uz', dest='ar')).text)
