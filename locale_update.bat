C:\Python27\Scripts\pybabel -v extract -F babel.config -o ./locale/messages.pot ./

REM C:\Python27\Scripts\pybabel init -l en_US -d ./locale -i ./locale/messages.pot
REM C:\Python27\Scripts\pybabel init -l zh_CN -d ./locale -i ./locale/messages.pot

C:\Python27\Scripts\pybabel update -l en_US -d ./locale/ -i ./locale/messages.pot
C:\Python27\Scripts\pybabel update -l zh_CN -d ./locale/ -i ./locale/messages.pot

REM C:\Python27\Scripts\pybabel compile -f -d ./locale
