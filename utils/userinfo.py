import web
from settings import db, render
import forms, helpers, auth

urls = (
    '/(.*)', 'userinfo'
    )

def get_password_form(user):
    #if the user has already set a password before, add the current password field to the form.
    form = forms.change_password()
    if user.password:
        curr_password = forms.curr_password
        form.inputs = (curr_password, ) + form.inputs
    return form    

class userinfo():
    def GET(self, uid, info_form=None, password_form=None):
        try:
            user = db.select('users', where='id=$uid', vars=locals())[0]
        except IndexError:     
            raise web.notfound
        
        info_form = info_form or forms.userinfo()
        if not password_form:
            password_form = get_password_form(user)
            
        info_form.fill(**user)
        msg, msg_type = helpers.get_delete_msg()
        return render.userpage(uid, info_form, password_form, msg)

    def POST(self, uid):
        if web.input('m', _method='GET'):
            return self.POST_password(uid)
        
        form = forms.userinfo()
        i = web.input()
        if form.validates(i):
            i.pop('submit')
            db.update('users', where='id=$uid', vars=locals(), **i)
            helpers.set_msg('User information updated.')
            raise web.seeother('/%s' % uid)
        else:
            return self.GET(uid, info_form=form)
    
    def POST_password(self, uid):
        user = db.select('users', what='password', where='id=$uid', vars=locals())[0]
        form = get_password_form(user)
        i = web.input()
        if form.validates(i):
            if ('curr_password' not in form) or auth.check_password(user, i.curr_password):
                enc_password = auth.encrypt_password(i.password)
                db.update('users', password=enc_password, verified=True, where='id=$uid', vars=locals())
                helpers.set_msg('Password saved.')
            else:
                helpers.set_msg('Invalid Password', 'error')    
            raise web.seeother('/%s' % uid)
        else:
             return self.GET(uid, password_form=form)   
            
app = web.application(urls, globals())
if __name__ == '__main__':
    app.run()            