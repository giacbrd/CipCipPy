#    CipCipPy - Twitter IR system for the TREC Microblog track.
#    Copyright (C) <2011-2013>  Giacomo Berardi, Andrea Esuli, Diego Marcheggiani
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""
CipCipPy

Indexing package.
"""

#FIXME clean all the duplicate code in the index functions

__version__ = "0.1"
__authors__ = ["Giacomo Berardi <giacomo.berardi@isti.cnr.it>", 
               "Andrea Esuli <andrea.esuli@isti.cnr.it>", 
               "Diego Marcheggiani <diego.marcheggiani@isti.cnr.it>"]

from ..config import INDEX_PATH
import os
import whoosh.index

def getIndexPath(name, tweetTime = None):
    return os.path.join(INDEX_PATH, name, str(tweetTime) if tweetTime else '')#date.strftime('%Y%m%d%H%M%S') if date else '')

def getIndex(indexName):
    """Returns a whoosh index"""
    return whoosh.index.open_dir(getIndexPath(indexName)).searcher()