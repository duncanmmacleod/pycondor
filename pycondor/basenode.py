
import os
import time
import glob

from . import utils


class BaseNode(object):

    def __init__(self, name, submit=None, extra_lines=None, verbose=0):

        # Validate user input
        if extra_lines and not isinstance(extra_lines, (str, list, tuple)):
            raise ValueError('extra_lines must be of type str, list, or tuple')
        elif extra_lines and isinstance(extra_lines, str):
            extra_lines = [extra_lines]

        self.name = utils.string_rep(name)
        self.submit = submit if submit is not None else os.getcwd()
        self.extra_lines = extra_lines
        self._built = False

        self.parents = []
        self.children = []

        # Set up logger
        self.logger = utils._setup_logger(self, verbose)

    def _get_fancyname(self):

        date = time.strftime('%Y%m%d')
        file_pattern = '{}/{}_{}_??.submit'.format(self.submit, self.name,
                                                   date)
        submit_number = len(glob.glob(file_pattern)) + 1
        fancyname = self.name + '_{}_{:02d}'.format(date, submit_number)

        return fancyname

    def _hasparent(self, node):
        return node in self.parents

    def add_parent(self, node):
        """Adds node to parents list

        Parameters
        ----------
        node : BaseNode
            Job or Dagman to append to the parents list.

        Returns
        -------
        self : object
            Returns self.

        """

        # Ensure that node is a BaseNode
        if not isinstance(node, BaseNode):
            raise ValueError(
                    'add_parent() is expecting a Job or Dagman instance.'
                    ' Got an object of type {}'.format(type(node)))

        # Don't bother continuing if node is already in the parents list
        if self._hasparent(node):
            return self

        # Add node to existing parents
        self.parents.append(node)
        self.logger.debug(
            'Added {} as a parent for {}'.format(node.name, self.name))

        # Add self instance as a child to the new parent node
        node.add_child(self)

        return self

    def add_parents(self, node_list):
        """Adds nodes to the parents list

        Parameters
        ----------
        args : list or tuple
            List of nodes to append to the parents list

        Returns
        -------
        self : object
            Returns self.

        """

        try:
            for node in node_list:
                self.add_parent(node)
        except:
            raise TypeError('add_parents() is expecting an iterable of '
                            'Job and/or Dagman objects')

        return self

    def _haschild(self, node):
        return node in self.children

    def add_child(self, node):
        """Adds node to children list

        Parameters
        ----------
        node : BaseNode
            Job or Dagman to append to the children list.

        Returns
        -------
        self : object
            Returns self.

        """

        # Ensure that node is a BaseNode
        if not isinstance(node, BaseNode):
            raise ValueError(
                    'add_child() is expecting a Job or Dagman instance.'
                    ' Got an object of type {}'.format(type(node)))

        # Don't bother continuing if node is already in the children list
        if self._haschild(node):
            return self

        # Add node to existing children
        self.children.append(node)
        self.logger.debug(
            'Added {} as a child for {}'.format(node.name, self.name))
        # Add this BaseNode instance as a parent to the new child node
        node.add_parent(self)

        return self

    def add_children(self, nodes):
        """Adds nodes to the children list

        Parameters
        ----------
        args : list or tuple
            List of nodes to append to the children list

        Returns
        -------
        self : object
            Returns self.

        """

        # Ensure that nodes is an iterable of type Job
        try:
            for node in nodes:
                self.add_child(node)
        except:
            raise TypeError('add_children() is expecting a list of '
                            'Jobs or Dagmans')

        return self

    def haschildren(self):
        """Checks for any children nodes

        Returns
        -------
        bool
            Returns whether or not this node has any child nodes.

        """
        return bool(self.children)

    def hasparents(self):
        """Checks for any parent nodes

        Returns
        -------
        bool
            Returns whether or not this node has any parent nodes.

        """
        return bool(self.parents)
