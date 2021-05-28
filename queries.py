from queries.QueryExecutor import ExamenAdmisionQueryExecutor, ExamenPruebaQueryExecutor
from queries import *
import sys
from os import path


#orig_stdout = sys.stdout
#f = open('out.txt', 'w')
#sys.stdout = f
#aquí va todo lo que quiero guardar en el txt
#sys.stdout = orig_stdout
#f.close()

a = ExamenAdmisionQueryExecutor
e = ExamenPruebaQueryExecutor

#a.bucketsAdmisionPorInstitucion([2],[1,2,3]) #passed
#a.bucketsAdmisionPorMunicipio([2],[15,237,169]) #passed
#a.bucketsAdmisionPorDepartamento([2],[1,2,3,10]) #passed
#a.bucketsAdmisionPais([2]) #passed
#e.bucketsPruebaPorInstitucion([1,2,5],[1],[2021]) #passed
#e.bucketsPruebaPorMunicipio([15,237,169],[1],[2021]) #passed
#e.bucketsPruebaPorDepartamento([1,2,3,10],[1],[2021]) #passed
#e.bucketsPruebaPais([1],[2021]) #passed
