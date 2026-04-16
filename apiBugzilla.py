import requests 

class Bugzilla:

    def __init__(self, API_KEY, url=None):

        self.Api_Key = API_KEY
        self.Headers = {'Accept': 'application/json'}
        if url:
            normalized = url.rstrip('/')
            if '/rest' in normalized:
                self.Url_Bugzilla = normalized + '/'
            elif '/demandas' not in normalized:
                self.Url_Bugzilla = normalized + '/demandas/rest/'
            else:
                self.Url_Bugzilla = normalized + '/rest/'
        else:
            self.Url_Bugzilla = 'https://vmbugzilla.altus.com.br/demandas/rest/'

        # REQUISIÇÕES CONDICIONAIS #
        # igual: "equals"
        # diferente: "notequals"
        # maior ou igual: "greaterthaneq"
    
    def MakeRequest(self, data, *include_fields):
        
        data['api_key'] = self.Api_Key
        if include_fields:
            data['include_fields'] = ','.join(include_fields)
       
        Url = self.Url_Bugzilla + 'bug'

        r = requests.get(Url, headers=self.Headers, params=data)

        if r.status_code == 200:

            dict = r.json()

            return dict['bugs']

                 

    
    def Get_Bug_Information(self, bug_id, *include_fields):

        data = {'id': bug_id, 'api_key': self.Api_Key}
        if include_fields:
            data['include_fields'] = ','.join(include_fields)

        Url = self.Url_Bugzilla + 'bug'

        r = requests.get(Url, headers=self.Headers, params=data)

        if r.status_code == 200:

            dict = r.json()

            return dict['bugs']
        
    def Get_Bug_Comment(self, bug_id):

        data = {'api_key': self.Api_Key}
        url = self.Url_Bugzilla.rstrip('/') + f'/bug/{bug_id}/comment'

        r = requests.get(url, headers=self.Headers, params=data)

        if r.status_code != 200:
            return []

        response = r.json()
        comments = []
        bug_comments = response.get('bugs', {}).get(str(bug_id), {}).get('comments', [])
        for comment in bug_comments:
            comments.append({
                'id': comment.get('id'),
                'author': comment.get('author'),
                'text': comment.get('text'),
                'creation_time': comment.get('creation_time')
            })

        return comments
        
    def Get_Activity_Information(self,activity,*include_fields):

        data = {'cf_activity':activity,'api_key':self.Api_Key,'include_fields':include_fields}

        Url = self.Url_Bugzilla + 'bug'

        r = requests.get(Url,headers=self.Headers,params=data)

        if r.status_code == 200:

            dict = r.json()

            return dict['bugs']
    
    ## Obtem QA Contact # 

    def Get_QAContact_Bugs(self,qa_contact,*include_fields):

        data = {'qa_contact':qa_contact,'api_key':self.Api_Key,'include_fields':include_fields}
       
        Url = self.Url_Bugzilla + 'bug' 

        r = requests.get(Url,headers=self.Headers,params=data)
      
        if r.status_code == 200:

            dict = r.json()
           
            return dict['bugs']
    
    def Get_Recuring_Activities_Information(self,rec_activity,*include_fields):

        data = {'v1':rec_activity,'o1':'substring','f1':'cf_recactivity','query_format':'advanced','api_key':self.Api_Key,'include_fields':include_fields}
       
        Url = self.Url_Bugzilla + 'bug' 

        r = requests.get(Url,headers=self.Headers,params=data)
      
        if r.status_code == 200:

            dict = r.json()
           
            return dict['bugs']
        
    def Get_Bug_History(self,bug_id,*include_fields):

        data = {'api_key':self.Api_Key,'include_fields':include_fields}

        Url = self.Url_Bugzilla + f'bug/{bug_id}/history'

        r = requests.get(Url,headers=self.Headers,params=data)

        if r.status_code == 200:

            dict = r.json()

            return dict['bugs']
        
    def Get_Resolution_Version_Information(self,resolution_version,*include_fields):

        data = {'cf_resolutionversion':resolution_version,'api_key':self.Api_Key,'include_fields':include_fields}

        Url = self.Url_Bugzilla + 'bug'

        r = requests.get(Url,headers=self.Headers,params=data)

        if r.status_code == 200:

            dict = r.json()

            return dict['bugs']
        
    def Get_Planned_Version_Information(self,resolution_version,*include_fields):

        data = {'cf_plannedversion':resolution_version,'api_key':self.Api_Key,'include_fields':include_fields}

        Url = self.Url_Bugzilla + 'bug'

        r = requests.get(Url,headers=self.Headers,params=data)

        if r.status_code == 200:

            dict = r.json()

            return dict['bugs']
        
    def Get_Resolution_Version_Information(self,product,resolution_version,*include_fields):

        data = {'product':product,'cf_resolutionversion':resolution_version,'api_key':self.Api_Key,'include_fields':include_fields}

        Url = self.Url_Bugzilla + 'bug'

        r = requests.get(Url,headers=self.Headers,params=data)

        if r.status_code == 200:

            dict = r.json()

            return dict['bugs']
    
    def Get_Resolution_Version_Range_Information(self,resolution_version_1,resolution_version_2,*include_fields):

        data = {'v1':resolution_version_1,'o1':'greaterthaneq','f1':'cf_resolutionversion','v2':resolution_version_2,'o2':'lessthaneq','f2':'cf_resolutionversion','query_format':'advanced','api_key':self.Api_Key,'include_fields':include_fields}

        Url = self.Url_Bugzilla + 'bug'

        r = requests.get(Url,headers=self.Headers,params=data)

        if r.status_code == 200:

            dict = r.json()

            return dict['bugs']
        
    def Get_Field_Information(self,field_name,field_values,*include_fields):

        data = {field_name:field_values,'api_key':self.Api_Key,'include_fields':include_fields}

        Url = self.Url_Bugzilla + 'bug'

        r = requests.get(Url,headers=self.Headers,params=data)

        if r.status_code == 200:

            dict = r.json()

            return dict['bugs']
        
    def Get_Product_Information(self,product,*include_fields):

        data = {'product':product,'api_key':self.Api_Key,'include_fields':include_fields}

        Url = self.Url_Bugzilla + 'bug'

        r = requests.get(Url,headers=self.Headers,params=data)

        if r.status_code == 200:

            dict = r.json()

            return dict['bugs']
        
    def Get_Component_Information(self,product,component,*include_fields):

        data = {'product':product,'component':component,'api_key':self.Api_Key,'include_fields':include_fields}

        Url = self.Url_Bugzilla + 'bug'

        r = requests.get(Url,headers=self.Headers,params=data)

        if r.status_code == 200:

            dict = r.json()

            return dict['bugs']
        
        
    def Get_Bugzilla_Users(self):

        data = {'names':'Altus','membership':True,'api_key':self.Api_Key}

        Url = self.Url_Bugzilla + r'group?'
        r = requests.get(Url,headers=self.Headers,params=data)
        if r.status_code == 200:

            dict = r.json()
            users = dict['groups'][0]['membership']
            names = [user['name'] for user in users if user ['email_enabled']]

        return names
