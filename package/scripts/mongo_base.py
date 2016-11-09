import os

from resource_management import *
import ambari_simplejson as json # simplejson is much faster comparing to Python 2.6 json module and has the same functions set.

class MongoBase(Script):
    db_file_path = '/etc/mongod.conf'
    config_file_path='/etc/mongod-config.conf'
    mongo_packages = None

    def installMongo(self, env):
        import params

        env.set_params(params)

        self.install_packages(env)

        print "Installing mongodb..."
        if self.mongo_packages is not None and len(self.mongo_packages):
            for pack in self.mongo_packages:
                Package(pack)      
        config_path = params.db_path + "/config"
        Execute(format('mkdir -p {config_path}'))

    def configureMongo(self, env):
        import params
        env.set_params(params)
        #db.conf
        mongod_db_content = InlineTemplate(params.mongod_db_content)   
        File(self.db_file_path, content=mongod_db_content)
        #config.conf
        mongod_config_content = InlineTemplate(params.mongod_config_content)   
        File(self.config_file_path, content=mongod_config_content)
        
        config_path = params.db_path + "/config"
        if os.path.exists(config_path):
            print "File exists"
        else:
            Execute(format('mkdir -p {config_path}'))

    def createDB(self, env):
        import params
        env.set_params(params)

        if params.db_name and params.db_pass:
            user_json = {'user': params.db_user, 'pwd': params.db_pass, 'roles': ['readWrite']}
            create_user_cmd = (
                "mongo {db} --eval 'db.getUser(\"{user}\")' | grep -q -w {db}\\.{user} || "
                "mongo {db} --eval 'db.createUser({json});'"
                )
            Execute(create_user_cmd.format(
                db=params.db_name,
                user=params.db_user,
                json=json.dumps(user_json)))
    def shutDown(self,env):
        import params
        Execute('find '+params.service_packagedir+' -iname "*.sh" | xargs chmod +x')
        cmd = format("{service_packagedir}/scripts/shutdown.sh {shutdown_port}")
        Execute(cmd,logoutput=True, ignore_failures=True)
