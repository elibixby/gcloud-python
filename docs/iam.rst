Using IAM For Users
===================

This document does not explain how Google Cloud IAM works, for that, please check out `the docs <https://cloud.google.com/iam/docs/>`_.

Resources that implement the IAM interface provide the following methods:

Policy Editing Methods
----------------------

>>> resource.add_roles(iam.user('alice@example.com'), resource.roles.OWNER, resource.roles.EDITOR)
True

The first argument is one of the IAM "Member" types:

- ``iam.user(email)`` an individual Google account
- ``iam.service_account(email)`` a Google Cloud Service Account
- ``iam.group(email)`` a Google group.
- ``iam.domain(domain_name)`` a Google-For-Work domain
- ``iam.ALL_AUTHENTICATED_USERS`` any authenticated user
- ``iam.ALL_USERS``

Note that all of these are convenience wrappers around strings. See the list of member string formats `here <https://cloud.google.com/iam/docs/managing-policies>`_.

All following arguments are roles to added to the specified member. Roles are simply strings that correspond to sets of permissions.
The resource should provide an enumeration of the possible "curated roles" for the resource.
You can acquire this list by running ``gcloud iam list-grantable-roles //fully/qualified/resource/path``.

This method returns ``True`` if the change to the resource's policy was made successfully, and returns ``False`` otherwise
(such as in the case of an update being made during this update).

>>> resource.remove_roles(iam.group('devs@example.com'), resource.roles.OWNER, resource.roles.EDITOR)
False

Same as above, but removes the specified roles from the specified member.

>>> resource.add_members(resource.roles.OWNER, iam.domain('example.com'), iam.service_account('compute@iam.my-project.example.com'))
True

Same as above, but the first argument is a role, and all subsequent arguments are members to which that role should be added.

>>> resource.remove_members(resource.roles.OWNER, iam.ALL_USERS)
True

Same as above, but removes all listed members from the specified role.


>>> user_emails = ['alice@example.com']
>>> def remove_fn(member):
>>>     return iam.is_group(member) or member == iam.user('bob@example.com')
>>> policy_change1 = iam.PolicyChange(resource.roles.OWNER).remove(iam.group('devs@example.com'))
>>> for user in user_emails:
>>>     policy_change1.add(iam.user(user))
>>> policy_change2 = iam.PolicyChange(resource.roles.EDITOR).remove(remove_fn=remove_fn)
>>> resource.update_policy(policy_change1, policy_change2)
True

If you need more complex logic to modify an IAM policy you can create a list of ``iam.PolicyChange`` s, and call ``resource.update_policy(...)``
with your policy changes.

A policy requires a ``role`` in the constructor, and provides two methods, ``add`` and ``remove``.
``add`` takes any number of members, and returns the ``iam.PolicyChange``. Note that this is just for convenience, state
is stored on the ``iam.PolicyChange`` object (see e.g. the looping usage).

``remove`` can also take any number of members, and returns the ``iam.PolicyChange``.
It can also take a ``remove_fn`` keyword argument, a function that takes a member string and returns whether or not it should
have the specified role. This function will be used to determine membership for all of the members that *currently* have
the specified role.

Just like above, this method returns True if the change was successfully made, or False otherwise. 

>>> resource.set_policy({resource.roles.OWNER: [iam.user('alice@example.com')],
>>>                      resource.roles.EDITOR: [(iam.user('alice@example.com'), (iam.user('charles@example.com')]})

Finally, you can manually set the policy of a resource. Use this only if you don't need any transactionality guarantees.
If updates are made to your policy during this change, they will be overwritten with exactly what is in your policy.


Policy Access Methods
---------------------

As seen above, IAM Policies are simply dictionaries, of the following form. 

``{role_string: [member_string, member_string], role_string...}``

>>> resource.get_policy()
{'roles/owner': ['user:alice@example.com')], 'roles/editor': [('user:alice@example.com'), ('user:charles@example.com')]}

As you can see, when printed out roles and members will not be distinguishable from strings, (because they are strings).

>>> resource.get_roles(iam.user('alice@example.com'))
['roles/owner', 'roles/editor']

Takes a member, returns a list of roles which the member has.

>>> resource.get_members(resource.roles.OWNER)
['user:alice@example.com', 'group:devs@example.com']

Takes a role, and returns a list of the members who have that role.

Using IAM For Contributors
==========================

TODO(elibixby)
