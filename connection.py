import sys

# add or modify if sys variables isn't detected
sys.path.append("C:/Users/czyl/Downloads/omniORB/omniORB-4.3.2/lib/python")
sys.path.append("C:/Users/czyl/Downloads/omniORB/omniORB-4.3.2/lib/x86_win32")

from omniORB import CORBA
import CosNaming
from boggled import PlayerServices

class Connection:
    def __init__(self):
        # initialize orb
        args = ["-ORBInitRef", "NameService=corbaname::localhost:2000"]
        self.orb = CORBA.ORB_init(args)

        # reference to the name service
        objref = self.orb.resolve_initial_references("NameService")
        self.naming_context = objref._narrow(CosNaming.NamingContext)

        if self.naming_context is None:
            print("Failed to narrow the root naming context")
            sys.exit(1)

        # look up
        name = [CosNaming.NameComponent("PlayerService", "")]

        # object reference from the name service
        try:
            obj = self.naming_context.resolve(name)
            self.player_service = obj._narrow(PlayerServices)
            if self.player_service is None:
                print("Object reference is not a PlayerServices")
                sys.exit(1)
        except CosNaming.NamingContext.NotFound:
            print("Name not found")
            sys.exit(1)
        except Exception as e:
            print(f"An error occurred during name resolution: {e}")
            sys.exit(1)

    def get_player_service(self):
        return self.player_service