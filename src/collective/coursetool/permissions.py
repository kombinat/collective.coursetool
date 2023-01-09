from Products.CMFCore.permissions import setDefaultRoles


# permission to register course member
RegisterMember = "collective.coursetool: Register member"
setDefaultRoles(RegisterMember, ("Manager", ))
