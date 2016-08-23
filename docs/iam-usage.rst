IAM User Guide
===================

.. note::
  This document assumes basic knowledge of Google Cloud IAM,
  see `the docs <https://cloud.google.com/iam/docs/>`_ for details

IAM Resources
-------------

The ``iam`` module provides a number of resources necessary for interacting with IAM.

Members
~~~~~~~
An IAM member is one of the following:

- ``iam.user(email)`` an individual Google account
- ``iam.service_account(email)`` a Google Cloud Service Account
- ``iam.group(email)`` a Google group.
- ``iam.domain(domain_name)`` a Google apps domain
- ``iam.ALL_AUTHENTICATED_USERS`` any authenticated Google user
- ``iam.ALL_USERS``

.. note::
  that all of these are convenience wrappers around strings.
  See the list of member string formats `here <https://cloud.google.com/iam/docs/managing-policies>`_.
  
Roles
~~~~~

Roles represent bundles of permissions that can be added to members.  For a complete list of roles available on a resource run 

``gcloud iam list-grantable-roles //fully/qualified/resource/path``

An ``iam.Role`` object has a name, title, and description

- An ``iam.Role.name`` is the canonical name of a role. This will be the value used as keys in policy dictionaries (see below), and will be referred to as the "role string" throughout this document. E.g. ``'roles/owner'``.
- ``iam.Role.title`` human readable title of the role. E.g. ``'Owner'``
- ``iam.Role.description`` the description of a role

Policies
~~~~~~~~

A policy is a dictionary from role strings to sets of members. ``resource.get_policy()`` also provides etags and versions. An etag is used to provide optimistic concurrency controls on policy updates, while versions are provided for end-user versioning.


Policy Changes
~~~~~~~~~~~~~~

An ``iam.PolicyChange`` object encapsulates changes to made to a policy transactionally. The ``iam.PolicyChange`` constructor takes an optional ``version`` keyword argument, an integer to use as the policy version. If ``version`` is ``None``, when applied ``iam.PolicyChange`` will increment whatever the current version of the policy is by 1.

To apply a ``iam.PolicyChange`` to a resource which implements the IAM interface call the ``apply()`` method with the resource as an argument. 

>>> policy_change = iam.PolicyChange(version=2).add(iam.roles.OWNER.name, [iam.user('alice@example.com')])
>>> policy, version, etag = policy_change.apply(resource)
>>> print(policy)
{'roles/owner': set(['user:alice@example.com'])}
>>> print(version)
2
>>> print(etag)
xDSFbfdasfAEFdfCds

Apply returns the new policy, it's version, and it's etag.

Optionally, a ``version`` keyword argument can be supplied to ``apply`` which will override the ``version`` behavior of the policy change.

>>> _, version, _ = policy_change.apply(resource, version=None)
>>> print(version)
3

Modifications can be added to a ``iam.PolicyChange`` object by one of two methods:

First the user can directly add or remove members from a ``Role``. ``iam.PolicyChange`` exposes two methods for this, ``add`` and ``remove`` which both take a role string or ``iam.Role`` object and a list of member strings.

>>> policy_change = iam.PolicyChange().add(iam.roles.OWNER, [iam.user('alice@example.com')])
>>> policy_change.remove(iam.roles.EDITOR, [iam.domain('example.com'), iam.group('devs@example.com')])
>>> policy, _, _ = policy_change.apply(resource)
>>> print(iam.user('alice@example.com') in policy[iam.roles.OWNER.name])
True
>>> print(iam.domain('example.com') in policy[iam.roles.EDITOR.name])
False

Second the user can specify a "membership function" which will take a member string as an argument, and return ``True`` if the member should belong to the specified role, and ``False`` otherwise.

>>> def membership_fn(member):
>>>     return not iam.is_group(member) or member == iam.user('bob@example.com')
>>> policy_change.fn(iam.roles.READER, membership_fn)
>>> policy, _, _ policy_change.apply(resource)
>>> print([member for member in policy[iam.roles.READER.name] if iam.is_group(member)])
['user:bob@example.com']


Methods
----------------------------------

Resources that implement the IAM interface provide the following methods:

Low Level Methods
~~~~~~~~~~~~~~~~~
Resources that implement IAM provide low level methods for interacting with IAM. 

``get_policy`` returns a tuple of ``(policy, version, etag)`` on the corresponding resource. 

>>> policy, version, etag = resource.get_policy()
>>> print(policy)
{
   'roles/owner': set(['user:alice@example.com']),
   'roles/editor: set(['group:admins@example.com']),
   'roles/reader': set(['domain:example.com', 'user:bob@example.com'])
}
>>> print(version)
5
>>> print(etag)
ffdFADFdsgfsjrsHTY

``set_policy`` takes a policy dictionary, as well as optional ``version`` and ``etag`` paramters. If updates are made to your policy during this change, they will be overwritten with exactly what is in your policy, or, if an etag is specified they will fail with a ``iam.ConcurrentModificationError``. ``iam.PolicyChange`` performs this "read-modify-write" cycle automatically for the user.

>>> policy['roles/owner'].add('user:charles@example.com')
>>> policy, version, etag = resource.set_policy(policy, etag=etag)
>>> print(version)
6

``missing_permissions`` takes an iterable of "permission strings" and returns those the user does not have on the resource

>>> resource.missing_permissions('resourcemanager.projects.get', 'resourcemanager.projects.delete')
set(['resourcemanager.projects.get'])

Returns permissions (if any), in the list that the user does not possess.

``query_grantable_roles()`` returns a list of ``iam.Role`` objects that represent roles (and their associated metadata)
which can be granted on the specified resource

>>> resource.query_grantable_roles()
[<Role>, <Role>, <Role>]

Convenience Methods
~~~~~~~~~~~~~~~~~~~

The following methods are wrappers around the creation and application of an ``iam.PolicyChange`` object. 

``add_role`` takes a single member, and a single ``iam.Role``, or role string, and adds the member to the role. ``add_role``

>>> resource.add_role(iam.user('alice@example.com'), iam.roles.OWNER.name)

``remove_role`` has the same signature as ``add_role`` but removes the member from the role.

>>> resource.remove_role(iam.user('bob@example.com'), iam.roles.OWNER.name)

``add_roles`` takes a single member, and an iterable of ``iam.Role`` s or role strings, and the member to each role

>>> resource.add_roles(iam.user('alice@example.com'), [iam.roles.OWNER.name, iam.roles.EDITOR.name])

``remove_roles`` has the same signature as ``resource.add_roles`` but removes all the specified roles from the member (where present)

>>> resource.remove_roles(iam.group('devs@example.com'), [iam.roles.OWNER.name, iam.roles.EDITOR.name])

``add_members`` takes an ``iam.Role`` and an iterable of members and adds each member to the role

>>> resource.add_members(iam.roles.OWNER.name, [iam.domain('example.com'), iam.service_account('compute@iam.my-project.example.com')])

``remove_members`` has the same signature as ``add_members`` but removes all the members from the specified role.

>>> resource.remove_members(iam.roles.OWNER.name, [iam.ALL_USERS])


IAM for Contributors
==========================

To add support for IAM to your resource, the following conditions must be met:

* The class must represent a resource that implements the IAM META API
* The object must provide a ``path`` property (a string that describes the canonical resource path)
* The object must provide a ``self._client`` member: An authenticated ``Client`` object

If all of these conditions are met, then IAM support can be added to your class by simply inheriting from the mixin

``class MyResource(iam._IAMMixin):``
