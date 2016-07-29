Using IAM For Users
===================

.. note:: This document assumes basic knowledge of Google Cloud IAM,
   see `the docs <https://cloud.google.com/iam/docs/>`_ for details

Resources that implement the IAM interface provide the following methods:

Policy Editing Convenience Methods
----------------------------------

Common keyword arguments:

- ``retries`` number of times to retry in the
   even of an interrupted transaction, (not available in ``set_policy``)
- ``version`` version number of the new policy. Not used for transactionality.


>>> resource.add_role(iam.user('alice@example.com'), iam.roles.OWNER.name)
True

The first argument is one of the IAM "Member" types:

- ``iam.user(email)`` an individual Google account
- ``iam.service_account(email)`` a Google Cloud Service Account
- ``iam.group(email)`` a Google group.
- ``iam.domain(domain_name)`` a Google apps domain
- ``iam.ALL_AUTHENTICATED_USERS`` any authenticated user
- ``iam.ALL_USERS``

.. note:: that all of these are convenience wrappers around strings.
   See the list of member string formats `here <https://cloud.google.com/iam/docs/managing-policies>`_.

The second argument is a role to added to the specified member. Roles are simply strings that correspond to sets of permissions.
The ``iam`` module provides a (possibly incomplete) list of curated roles.
You can acquire the complete list by running ``gcloud iam list-grantable-roles //fully/qualified/resource/path``, and use the
names provided there in place of ``iam.roles.XXXX.name`` wherever the latter is used in this doc.

This method returns ``True`` if the change to the resource's policy was made successfully, and returns ``False`` otherwise
(such as in the case of an update being made during this update).

>>> resource.remove_role(iam.user('bob@example.com'), iam.roles.OWNER.name)
True


>>> resource.add_roles(iam.user('alice@example.com'), [iam.roles.OWNER.name, iam.roles.EDITOR.name])
True

Same as ``resource.add_role`` the second argument is a list of roles to be added to the specified member.

>>> resource.remove_roles(iam.group('devs@example.com'), [iam.roles.OWNER.name, iam.roles.EDITOR.name])
False

Same as above, but removes the specified roles from the specified member.

>>> resource.add_members(iam.roles.OWNER.name, [iam.domain('example.com'), iam.service_account('compute@iam.my-project.example.com')])
True

The first argument is a role, and the second argument is a list of members to be added to that role.

>>> resource.remove_members(iam.roles.OWNER.name, iam.ALL_USERS)
True

Same as above, but removes all listed members from the specified role.

>>> def remove_fn(member):
>>>     return iam.is_group(member) or member == iam.user('bob@example.com')
>>> policy_change = iam.PolicyChange(version=2).add(iam.roles.OWNER.name, [iam.user('alice@example.com')])
>>> policy_change.remove(iam.roles.EDITOR.name, [iam.domain('example.com'), iam.group('devs@example.com')])
>>>              .remove_fn(iam.roles.READER.name, remove_fn)
>>> policy_change.apply(resource)
True

If you need more complex logic to modify an IAM policy you can create a ``iam.PolicyChange`` object. ``PolicyChange`` takes
an optional ``version`` keyword argument which specifies which version the updated policy should be considered.

``iam.PolicyChange`` exposes four methods. ``add`` and ``remove`` take a role, and a list of members, and add, or remove
those members from the specified roll respectively. They have the same signature as ``resource.add_members`` and ``resource.remove_members`` respectively.
``remove_fn`` takes a role and a function object as arguments.
The provided function takes a ``member`` string and returns whether or not the member should have the specified role.

Finally, ``iam.PolicyChange`` exposes an ``apply`` method, which takes a resource, and applies the change to the resource.

Just like above, this method returns True if the change was successfully made, or False otherwise. 

>>> resource.set_policy(
>>>     {
>>>         iam.roles.OWNER.name: [iam.user('alice@example.com')],
>>>         iam.roles.EDITOR.name: [(iam.user('alice@example.com'), (iam.user('charles@example.com')]
>>>     },
>>>     etag=XXXXXX,
>>>     version=0
>>>)

Finally, you can manually set the policy of a resource.
``set_policy`` takes a policy, and optionally an ``etag`` string, and version number.

Version is provided for end-user use, while etag can be used to guarantee transactionality.


Use this only if you don't need any transactionality guarantees, or want to handle transactionality yourself, using etag.

If updates are made to your policy during this change, they will be overwritten with exactly what is in your policy.
Or, if an etag is specified they will fail with a ``TransactionInterruptedException``


Policy Access Methods
---------------------

As seen above, IAM Policies are simply dictionaries, of the following form.

``{role_string: [member_string, member_string], role_string...}``

>>> resource.get_policy()
{'roles/owner': ['user:alice@example.com')], 'roles/editor': [('user:alice@example.com'), ('user:charles@example.com')]}, 0, XXXXX

``get_policy`` returns a tuple ``policy, version, etag``

As you can see, when printed out roles and members will not be distinguishable from strings, (because they are strings).

>>> resource.get_roles(iam.user('alice@example.com'))
['roles/owner', 'roles/editor']

Takes a member, returns a list of roles which the member has.

>>> resource.get_members(iam.roles.OWNER.name)
['user:alice@example.com', 'group:devs@example.com']

Takes a role, and returns a list of the members who have that role.

Misc Methods
------------

>>> iam.missing_permission(resource, permissions)
[permission1, permission2]

Returns permissions (if any), in the specified list that the user does not possess.

>>> iam.grantable_roles(resource)
[<Role>, <Role>, <Role>]

Returns a list of ``iam.Role`` objects that represent roles (and their associated metadata)
which can be granted on the specified resource

``iam.Role`` objects provide three properties, a ``name`` , ``title`` , and ``description`` .

Using IAM For Contributors
==========================

TODO(elibixby)
