# Copyright 2001 by Tarjei Mikkelsen.  All rights reserved.
# This code is part of the Biopython distribution and governed by its
# license.  Please see the LICENSE file that should have been included
# as part of this package.

"""KEGG Enzyme package

This module provides code to work with the KEGG Enzyme database.


Classes:
Record
Iterator
Parser

_Scanner
_Consumer

"""

# XML from python
from xml.sax import handler

# Martel
import Martel
from Martel import RecordReader

# other Biopython stuff
from Bio import File
from Bio.KEGG import _write_kegg
from Bio.KEGG import _wrap_kegg
from Bio.ParserSupport import AbstractConsumer
from Bio.ParserSupport import EventGenerator

import enzyme_format

# Set up line wrapping rules (see Bio.KEGG._wrap_kegg)
rxn_wrap = [0, "",
            (" + ","",1,1),
            (" = ","",1,1),
            (" ","$",1,1),
            ("-","$",1,1)]
name_wrap = [0, "",
             (" ","$",1,1),
             ("-","$",1,1)]
id_wrap = lambda indent : [indent, "",
                           (" ","",1,0)]
struct_wrap = lambda indent : [indent, "",
                               ("  ","",1,1)]
motif_wrap = lambda indent : [indent, "",
                              ("-","",1,1)]

class Record:
    """Holds info from a KEGG Enzyme record.

    Members:
    entry       The EC number (withou the 'EC ').
    name        A list of the enzyme names.
    classname   A list of the classification terms.
    sysname     The systematic name of the enzyme.
    reaction    A list of the reaction description strings.
    substrate   A list of the substrates.
    product     A list of the products.
    inhibitor   A list of the inhibitors.
    cofactor    A list of the cofactors.
    effector    A list of the effectors.
    comment     A list of the comment strings.
    pathway     A list of 3-tuples: (database, id, pathway)
    genes       A list of 2-tuples: (organism, list of gene ids)
    disease     A list of 3-tuples: (database, id, disease)
    motif       A list of 3-tuples: (database, id, motif)
    structures  A list of 2-tuples: (database, list of struct ids)
    dblinks     A list of 2-tuples: (database, list of db ids)
    """
    def __init__(self):
        """__init___(self)

        Create a new Record.
        """
        self.entry      = ""
        self.name       = []
        self.classname  = []
        self.sysname    = []
        self.reaction   = []
        self.substrate  = []
        self.product    = []
        self.inhibitor  = []
        self.cofactor   = []
        self.effector   = []
        self.comment    = []
        self.pathway    = []
        self.genes      = []
        self.disease    = []
        self.motif      = []
        self.structures = []
        self.dblinks    = []
    def __str__(self):
        """__str__(self)

        Returns a string representation of this Record.
        """
        return self._entry() + \
               self._name()  + \
               self._classname() + \
               self._sysname() + \
               self._reaction() + \
               self._substrate() + \
               self._product() + \
               self._inhibitor() + \
               self._cofactor() + \
               self._effector() + \
               self._comment() + \
               self._pathway() + \
               self._genes() + \
               self._disease() + \
               self._motif() + \
               self._structures() + \
               self._dblinks() + \
               "///"
    def _entry(self):
        return _write_kegg("ENTRY",
                           ["EC " + self.entry])
    def _name(self):
        return _write_kegg("NAME",
                           map(lambda l:
                               _wrap_kegg(l, wrap_rule = name_wrap),
                               self.name))
    def _classname(self):
        return _write_kegg("CLASS",
                           self.classname)
    def _sysname(self):
        return _write_kegg("SYSNAME",
                           [_wrap_kegg(l, wrap_rule = name_wrap) \
                            for l in self.sysname])
    def _reaction(self):
        return _write_kegg("REACTION",
                           [_wrap_kegg(l, wrap_rule = rxn_wrap) \
                            for l in self.reaction])
    def _substrate(self):
        return _write_kegg("SUBSTRATE",
                           [_wrap_kegg(l, wrap_rule = name_wrap) \
                            for l in self.substrate])
    def _product(self):
        return _write_kegg("PRODUCT",
                           [_wrap_kegg(l, wrap_rule = name_wrap) \
                            for l in self.product])
    def _inhibitor(self):
        return _write_kegg("INHIBITOR",
                           [_wrap_kegg(l, wrap_rule = name_wrap) \
                            for l in self.inhibitor])
    def _cofactor(self):
        return _write_kegg("COFACTOR",
                           [_wrap_kegg(l, wrap_rule = name_wrap) \
                            for l in self.cofactor])
    def _effector(self):
        return _write_kegg("EFFECTOR",
                           [_wrap_kegg(l, wrap_rule = name_wrap) \
                            for l in self.effector])
    def _comment(self):
        return _write_kegg("COMMENT",
                           [_wrap_kegg(l, wrap_rule = id_wrap(0)) \
                            for l in self.comment])
    def _pathway(self):
        s = []
        for entry in self.pathway:
            s.append(entry[0] + ": " + entry[1] + "  " + entry[2])
        return _write_kegg("PATHWAY",
                           [_wrap_kegg(l, wrap_rule = id_wrap(16)) \
                            for l in s])
    def _genes(self):
        s = []
        for entry in self.genes:
            s.append(entry[0] + ": " + " ".join(entry[1]))
        return _write_kegg("GENES",
                           [_wrap_kegg(l, wrap_rule = id_wrap(5)) \
                            for l in s])
    def _disease(self):
        s = []
        for entry in self.disease:
            s.append(entry[0] + ": " + entry[1] + "  " + entry[2])
        return _write_kegg("DISEASE",
                           [_wrap_kegg(l, wrap_rule = id_wrap(13)) \
                            for l in s])    
    def _motif(self):
        s = []
        for entry in self.motif:
            s.append(entry[0] + ": " + entry[1] + "  " + entry[2])
        return _write_kegg("MOTIF",
                           [_wrap_kegg(l, wrap_rule = motif_wrap(13)) \
                            for l in s])
    def _structures(self):
        s = []
        for entry in self.structures:
            s.append(entry[0] + ": " + "  ".join(entry[1]) + "  ")
        return _write_kegg("STRUCTURES",
                           [_wrap_kegg(l, wrap_rule = struct_wrap(5)) \
                            for l in s])
    def _dblinks(self):
        # This is a bit of a cheat that won't work if enzyme entries
        # have more than one link id per db id. For now, that's not
        # the case - storing links ids in a list is only to make
        # this class similar to the Compound.Record class.
        s = []
        for entry in self.dblinks:
            s.append(entry[0] + ": " + entry[1][0])
        return _write_kegg("DBLINKS", s)


class Iterator:
    """Iterator to read a file of KEGG Enzyme entries one at a time.
    """
    def __init__(self, handle, parser = None):
        """Initialize the iterator.

        Arguments:
        o handle - A handle with Enzyme entries to iterate through.
        o parser - An optional parser to pass the entries through before
        returning them. If None, then the raw entry will be returned.
        """
        self._reader = RecordReader.EndsWith(handle, "///")          
        self._parser = parser

    def next(self):
        """Return the next KEGG Enzyme record from the handle.

        Will return None if we ran out of records.
        """
        data = self._reader.next()
        if self._parser is not None:
            if data:
                return self._parser.parse(File.StringHandle(data))
        return data


class Parser:
    """Parse KEGG Enzyme files into Record objects
    """
    def __init__(self, debug_level = 0):
        """Initialize the parser.

        Arguments:
        o debug_level - An optional argument that species the amount of
        debugging information Martel should spit out. By default we have
        no debugging info (the fastest way to do things), but if you want
        you can set this as high as two and see exactly where a parse fails.
        """
        self._scanner = _Scanner(debug_level)

    def parse(self, handle):
        """Parse the specified handle into a KEGG Enzyme record.
        """
        self._consumer = _Consumer()
        self._scanner.feed(handle, self._consumer)
        return self._consumer.data


class _Consumer(AbstractConsumer):
    """Create a KEGG Enzyme Record from scanner events.

    """
    def __init__(self):
        self.data = Record()
        self._current_path         = []
        self._current_organism     = ""
        self._current_motif        = []
        self._current_disease      = []
        self._current_dblinks      = []
        self._current_structure_db = ""
    def _unwrap(self, data, add_space = 0):
        lines = data.split("\n")
        if len(lines) == 1:
            return data
        else:
            s = ""
            for l in lines:
                l = l.lstrip()
                if add_space and l[0] != "$" and s[-1] != " ":
                    l = " " + l
                elif l[0] == "$":
                    l = l[1:]
                s = s + l
        return s
    def entry(self, entry):
        self.data.entry = entry[0][3:]
    def name(self, name):
        self.data.name = map(self._unwrap, name)
    def classname(self, classname):
        self.data.classname = classname
    def sysname(self, sysname):
        self.data.sysname = map(self._unwrap, sysname)
    def reaction(self, reaction):
        self.data.reaction = reaction
    def substrate(self, substrate):
        self.data.substrate = map(self._unwrap, substrate)
    def product(self, product):
        self.data.product = map(self._unwrap, product)
    def inhibitor(self, inhibitor):
        self.data.inhibitor = map(self._unwrap, inhibitor)
    def cofactor(self, cofactor):
        self.data.cofactor = map(self._unwrap, cofactor)
    def effector(self, effector):
        self.data.effector = map(self._unwrap, effector)
    def comment(self, comment):
        self.data.comment = comment
    def pathway_db(self, pathway_db):
        self._current_path.append(pathway_db[0])
    def pathway_id(self, pathway_id):
        self._current_path.append(pathway_id[0])
    def pathway_desc(self, pathway_desc):
        self._current_path.append(" ".join(pathway_desc))
        self.data.pathway.append(tuple(self._current_path))
        self._current_path = []
    def organism(self, organism):
        self._current_organism = organism[0]
    def gene_id(self, gene_id):
        self.data.genes.append((self._current_organism, gene_id))
        self._current_organism = ""
    def disease_db(self, disease_db):
        self._current_disease.append(disease_db[0])
    def disease_id(self, disease_id):
        self._current_disease.append(disease_id[0])
    def disease_desc(self, disease_desc):
        self._current_disease.append(" ".join(disease_desc))
        self.data.disease.append(tuple(self._current_disease))
        self._current_disease = []    
    def motif_db(self, motif_db):
        self._current_motif.append(motif_db[0])
    def motif_id(self, motif_id):
        self._current_motif.append(motif_id[0])
    def motif(self, motif):
        self._current_motif.append(self._unwrap(motif[0]))
        self.data.motif.append(tuple(self._current_motif))
        self._current_motif = []
    def structure_db(self, structure_db):
        self._current_structure_db = structure_db[0]
    def structure_id(self, structure_id):
        self.data.structures.append((self._current_structure_db, structure_id))
        self._current_structure_db = ""
    def dblinks_db(self, dblinks_db):
        self._current_dblinks.append(dblinks_db[0])
    def dblinks_id(self, dblinks_id):
        self._current_dblinks.append(dblinks_id)
        self.data.dblinks.append(tuple(self._current_dblinks))
        self._current_dblinks = []
    def record_end(self, end):
        pass


def _strip(line_list):
    """Combine multiple lines of content separated by spaces.

    This function is used by the EventGenerator callback function to
    combine multiple lines of information. The lines are stripped to
    remove whitespace.
    """
    # first strip out extra whitespace
    return [x.strip() for x in line_list]
      

class _Scanner:
    """Start up Martel to do the scanning of the file.

    This initialzes the Martel based parser and connects it to a handler
    that will generate events for a Consumer.
    """
    def __init__(self, debug = 0):
        """Initialize the scanner by setting up our caches.

        Arguments:
        o debug - The level of debugging that the parser should display.
                  Level 0 is no debugging, Level 2 displays the most
                  debugging info (but is much slower).
                  See Martel documentation for more info on this.
        """
        # a listing of all tags we are interested in scanning for
        # in the Martel parser
        self.interest_tags = ["entry", "name", "classname", "sysname",
                              "reaction", "substrate", "product",
                              "inhibitor", "cofactor", "effector",
                              "comment", 
                              "pathway_db", "pathway_id", "pathway_desc",
                              "organism", "gene_id",
                              "disease_db", "disease_id", "disease_desc",
                              "motif_db", "motif_id", "motif",
                              "structure_db", "structure_id",
                              "dblinks_db", "dblinks_id",
                              "record_end"]

        # make a parser that returns only the tags we are interested in
        expression = Martel.select_names(enzyme_format.record,
                                         self.interest_tags)
        self._parser = expression.make_parser(debug_level = debug)

    def feed(self, handle, consumer):
        """Feeed a set of data into the scanner.

        Arguments:
        o handle - A handle with the information to parse.
        o consumer - The consumer that should be informed of events.
        """
        self._parser.setContentHandler(EventGenerator(consumer,
                                                      self.interest_tags,
                                                      _strip))
        self._parser.setErrorHandler(handler.ErrorHandler())
        self._parser.parseFile(handle)


