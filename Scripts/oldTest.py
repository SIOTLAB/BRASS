
import eossdk
import sys

class TestAgent(eossdk.AgentHandler, eossdk.MacTableHandler):
   def __init__(self, sdk):
      self.agentMgr = sdk.get_agent_mgr()
      self.tracer = eossdk.Tracer("HelloWorldPythonAgent")
      eossdk.AgentHandler.__init__(self, self.agentMgr)

      self.macMgr = sdk.get_mac_table_mgr()
      eossdk.MacTableHandler.__init__(self, self.macMgr)
      self.tracer.trace0("Python agent constructed")

   def on_initialized(self):
      self.tracer.trace0("Initialized")
      name = self.agentMgr.agent_option("name")
      self.watch_all_mac_entries(True)
      if not name:
         # No name initially set
         self.agentMgr.status_set("greeting", "Welcome! What is your name?")
      else:
         # Handle the initial state
         self.on_agent_option("name", name)

   def on_agent_option(self, optionName, value):
      if optionName == "name":
         if not value:
            self.tracer.trace3("Name deleted")
            self.agentMgr.status_set("greeting", "Goodbye!")
         else:
            # Time for some social networking!
            self.tracer.trace3("Saying hi to %s" % value)
            self.agentMgr.status_set("greeting", "Hello %s!" % value)

   def on_agent_enabled(self, enabled):
      if not enabled:
         self.tracer.trace0("Shutting down")
         self.agentMgr.status_set("greeting", "Adios!")
         self.agentMgr.agent_shutdown_complete_is(True)

   def on_mac_entry_set(self, entry):
      self.tracer.trace9("On mac entry set")
      vlan_id = entry.mac_key().vlan_id()
      eth_addr = entry.mac_key().eth_addr()
      self.macMgr.status_set(eth_addr, vlan_id)
      #  t.trace9(__PRETTY_FUNCTION__);
      #  std::string vlan_id = std::to_string(int(entry.mac_key().vlan_id()));
      #  std::string eth_addr = entry.mac_key().eth_addr().to_string();
      #  agent_mgr_->status_set(eth_addr.c_str(),
      #                         vlan_id.c_str());

if __name__ == "__main__":
   sdk_ = eossdk.Sdk()
   # Assign the agent instance to a variable so it remains in scope and
   # is not deleted:
   _ = HelloWorldAgent(sdk_)
   sdk_.main_loop(sys.argv)
