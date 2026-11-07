import tempfile, unittest
from pathlib import Path
from queue import connect, enqueue, work_once
class QueueTest(unittest.TestCase):
 def test_persist_and_run(self):
  with tempfile.TemporaryDirectory() as d:
   path=Path(d)/"queue.db"; db=connect(path)
   jid=enqueue(db,"kiro","story_outline",{"idea":"Test"})
   db.close();db=connect(path)
   self.assertEqual(work_once(db),jid)
   row=db.execute("SELECT status,result FROM jobs WHERE id=?",(jid,)).fetchone()
   self.assertEqual(row[0],"done")
   self.assertIn("offline_template_only",row[1])
 def test_no_auto_publish(self):
  with tempfile.TemporaryDirectory() as d:
   db=connect(Path(d)/"queue.db")
   jid=enqueue(db,"zek","quality_gate",{})
   work_once(db)
   self.assertIn('"auto_publish": false',db.execute("SELECT result FROM jobs WHERE id=?",(jid,)).fetchone()[0])
 def test_unknown_job_fails_safely(self):
  with tempfile.TemporaryDirectory() as d:
   db=connect(Path(d)/"queue.db")
   jid=enqueue(db,"nox","unknown",{})
   work_once(db)
   self.assertEqual(db.execute("SELECT status FROM jobs WHERE id=?",(jid,)).fetchone()[0],"failed")
if __name__=="__main__":unittest.main()
