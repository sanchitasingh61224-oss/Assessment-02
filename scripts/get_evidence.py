import re,os,random,csv,subprocess,json
import multiprocessing as mp
try:
    from .utils import *
except ImportError:  # pragma: no cover - direct script execution fallback
    from utils import *
try:
    from .check_rule_KB import *
except ImportError:  # pragma: no cover - direct script execution fallback
    from check_rule_KB import *




from SPARQLWrapper import SPARQLWrapper, JSON

import hashlib

QUERY_TIMEOUT_SECONDS = 10

CACHE_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "dbpedia_cache")
os.makedirs(CACHE_DIR, exist_ok=True)

ENDPOINTS = (
    "https://dbpedia.org/sparql",
    "http://dbpedia.org/sparql",
)


def _cache_path_for_query(query):
    digest = hashlib.sha256(query.encode("utf-8")).hexdigest()
    return os.path.join(CACHE_DIR, digest + ".json")


def _read_cache(query):
    cache_path = _cache_path_for_query(query)
    if not os.path.exists(cache_path):
        return None
    try:
        with open(cache_path, "r", encoding="utf-8") as fh:
            return json.load(fh)
    except (OSError, ValueError):
        return None


def _write_cache(query, payload):
    cache_path = _cache_path_for_query(query)
    with open(cache_path, "w", encoding="utf-8") as fh:
        json.dump(payload, fh, ensure_ascii=False)


def _sparql_worker(endpoint, query, queue_obj):
    try:
        sparql = SPARQLWrapper(endpoint)
        sparql.setTimeout(QUERY_TIMEOUT_SECONDS)
        sparql.setQuery(query)
        sparql.setReturnFormat(JSON)
        results = sparql.query().convert()
        bindings = results.get("results", {}).get("bindings", [])
        queue_obj.put({"bindings": bindings})
    except Exception as exc:  # pragma: no cover - defensive fallback
        queue_obj.put({"error": repr(exc)})


def _execute_query_with_timeout(endpoint, query):
    ctx = mp.get_context("spawn")
    queue_obj = ctx.Queue()
    proc = ctx.Process(target=_sparql_worker, args=(endpoint, query, queue_obj))
    proc.start()
    proc.join(QUERY_TIMEOUT_SECONDS)
    if proc.is_alive():
        proc.terminate()
        proc.join(1)
        raise TimeoutError(f"DBpedia query timed out after {QUERY_TIMEOUT_SECONDS}s for {endpoint}")
    if queue_obj.empty():
        raise RuntimeError(f"DBpedia worker returned no response for {endpoint}")
    payload = queue_obj.get()
    if "error" in payload:
        raise RuntimeError(payload["error"])
    return payload["bindings"]


def _execute_sparql_query(query):
    cached = _read_cache(query)
    if cached is not None:
        return cached

    last_error = None
    for endpoint in ENDPOINTS:
        try:
            bindings = _execute_query_with_timeout(endpoint, query)
            if bindings:
                _write_cache(query, bindings)
                return bindings
            last_error = RuntimeError("DBpedia returned no bindings")
        except Exception as exc:  # pragma: no cover - defensive fallback
            last_error = exc
            continue

    if last_error is not None:
        print(f"DBpedia query failed after retries: {type(last_error).__name__}: {last_error}")
    return []


sparql = SPARQLWrapper("https://dbpedia.org/sparql")





sparql_endpoint ='http://dbpedia.org/sparql' #'http://localhost:8890/sparql'
prefix = 'PREFIX dbo:  <http://dbpedia.org/ontology/>  select '
prefix2 = 'PREFIX dbp:  <http://dbpedia.org/property/>  select '



def get_evidence_query(relations, vars, resource):
    where = ' where  { '
    select = ''
    triple = ''
    for r, rel in enumerate(relations):
        select += '  ?' + vars[r].split(',')[0].lower() + ', dbo:' + rel + ', ?' + vars[r].split(',')[1].lower() + ' ,'
        triple += '  ?' + vars[r].split(',')[0].lower() + ' dbo:' + rel + ' ?' + vars[r].split(',')[1].lower() + ' .'
    end = ' }'
    query = prefix + select[:-1] + where + triple + end
    query_new = query.replace('?a', '<http://dbpedia.org/resource/' + resource[0] + '>')
    query_new = query_new.replace('?b', '<http://dbpedia.org/resource/' + resource[1] + '>')
    return query_new

def get_evidence_query_2(relations, vars, resource):
    where = ' where  { '
    select = ''
    triple = ''
    for r, rel in enumerate(relations):
        select += '  ?' + vars[r].split(',')[0].lower() + ', dbp:' + rel + ', ?' + vars[r].split(',')[1].lower() + ' ,'
        triple += '  ?' + vars[r].split(',')[0].lower() + ' dbp:' + rel + ' ?' + vars[r].split(',')[1].lower() + ' .'
    end = ' }'
    query = prefix2 + select[:-1] + where + triple + end
    query_new = query.replace('?a', '<http://dbpedia.org/resource/' + resource[0] + '>')
    query_new = query_new.replace('?b', '<http://dbpedia.org/resource/' + resource[1] + '>')
    return query_new


def get_evidence(resource, rules):
    evidence = []
    num_evid_found=0
    for rule in rules:
 #       print("#########################################################")
#        print(rule)
        if ':-' in rule and rule[:2] != ':-':
            body = rule.split(':-')[1].replace('not','')
            body=re.sub(r'type\(.*?\)','',body)
            #print(body)
            relations = re.findall(r"(\w*?)\(", body)
            vars = re.findall(r"\((.*?)\)", body)
            #print(relations)
            #print(vars)
            query = get_evidence_query(relations, vars, resource)
            query2 = get_evidence_query_2(relations, vars, resource)

            #print(query)
 #           print(type(query))

            q1_values=[]
            try:
                results = _execute_sparql_query(query)
                for result in results:
                    s=[]
                    for key in result.keys():
                        s.append(result[key]['value'])
                    q1_values.append(s)
            except Exception:
                q1_values=[]

            q2_values=[]
            try:
                results = _execute_sparql_query(query2)
                for result in results:
                    s=[]
                    for key in result.keys():
                        s.append(result[key]['value'])
                    q2_values.append(s)
            except Exception:
                q2_values=[]
            if q1_values:
                #print("Q1 values",q1_values)
                for vals in q1_values:
                    try:
                        vals = [val.split('/')[-1] if '/' in val else val for val in vals]
                        #print("VALS",vals)
                        evid = [vals[i:i + 3] for i in range(0, len(vals), 3)]
                        #print("EVIDS",evid)
                        evidence.extend(evid)
                        #print("HHHHHOOOOO")
                        #print("EVIDENCE",evidence)
                    except:
                        pass

            if q2_values:
                for vals in q2_values:
                    try:
                        vals = [val.split('/')[-1] if '/' in val else val for val in vals]
                        evid = [vals[i:i + 3] for i in range(0, len(vals), 3)]
                        evidence.extend(evid)
                    except:
                        pass



    return evidence


def get_type_sub_obj(resource):
    evidence=[]
    for j in range(len(resource)):
        query1='''select distinct ?o where { <http://dbpedia.org/resource/'''+resource[j]+'''> rdf:type ?o .
    FILTER (strstarts(str(?o), "http://dbpedia.org/ontology/"))
    }'''


        q1_values=[]
        try:
            results = _execute_sparql_query(query1)
            for result in results:
                s=[]
                for key in result.keys():
                    s.append(result[key]['value'])
                q1_values.append(s)
        except Exception:
            q1_values=[]
        if q1_values:
            for vals in q1_values:
                try:
                    vals = [val.split('/')[-1] if '/' in val else val for val in vals]
                    evid= [vals[i:i + 3] for i in range(0, len(vals), 3)]
#                    print(evid[0][0],"dlkkdkd")
                    evidence.append('type("'+resource[j]+'",'+'"'+evid[0][0]+'"'+').\n')
 #                   print(evidence)
                except:
                    pass

        query2='''select distinct ?o where { <http://dbpedia.org/resource/'''+resource[j]+'''> rdf:type ?o .
    FILTER (strstarts(str(?o), "http://www.w3.org/2002/07/owl#"))
    }'''


        q2_values=[]
        try:
            results = _execute_sparql_query(query2)
            for result in results:
                s=[]
                for key in result.keys():
                    s.append(result[key]['value'])
                q2_values.append(s)
        except Exception:
            q2_values=[]
        #print(resource[j],q2_values)
        if q2_values:
            for vals in q2_values:
                try:
                    vals = [val.split('/')[-1] if '/' in val else val for val in vals]
                    evid= [vals[i:i + 3] for i in range(0, len(vals), 3)]
#                    print(evid[0][0],"dlkkdkd")
                    evidence.append('type("'+resource[j]+'",'+'"'+evid[0][0]+'"'+').\n')
 #                   print(evidence)
                except:
                    pass

#    print(evidence)
    return evidence




def adjust_evidence_form(evids):
    adjusted_evid=[]

    for evid in evids:
        adjusted_evid.append(evid[1]+'('+'"'+evid[0]+'"'+','+'"'+evid[2]+'"'+')'+'.'+'\n')

    return  list(set(adjusted_evid))



#at least one rule satisfied
def generate_evid_KB_grounded(rules_file,claims_file,dir,evid_dir,N=100):

    if not os.path.exists(dir):
        os.makedirs(dir)

    if not os.path.exists(evid_dir):
        os.makedirs(evid_dir)



    with open(rules_file,'r', encoding='utf-8', errors='replace') as f:
        rules=f.readlines()

    num_pos=0
    num_neg=0
    clm=[]
    with open(claims_file,'r', encoding='utf-8', errors='replace') as f:
        lines=f.readlines()
    for line in lines[:]:
        print("############################################")
        print(line)
        #print(num_pos,num_neg)
        if(line):
            id=line.split(',')[0]
            if(id+'er_unique.txt' in os.listdir(evid_dir)):
                num_pos+=1
                continue
            resource=[line.split(',')[1],line.split(',')[2]]
            subject,object=resource
            label=int(line.split(',')[3])
            if((label==1 and num_pos<N) or (label==0 and num_neg<N)):
                sparql_evid=get_evidence(resource,rules)
                if(len(sparql_evid)!=0):
                    if(label==1 and num_pos<N):
                        evids=adjust_evidence_form(sparql_evid)
                        type_evids=get_type_sub_obj(resource)


                        evids_literals=set()
                        for evd in evids:
                            l=get_literals(evd)
                            for ll in l:
                                evids_literals.add(ll)
                        if(subject in evids_literals):
                            evids_literals.remove(subject)
                        if(object in evids_literals):
                            evids_literals.remove(object)



                        if(check_KB_evid_rules(rules,evids,evids_literals,subject,object)):
                            num_pos+=1
                            clm.append(line)
                            print(line)
                            print(num_pos,num_neg)

                            f=open(evid_dir+id+'er_unique.txt','w')
                            for rule in rules:
                                f.write(rule)

                            for evid in evids:
                                f.write(evid)

                            for evid in type_evids:
                                if('owl#' in evid):
                                    evid=evid.replace('owl#','')
                                f.write(evid)

                            f.close()

                    if(label==0 and num_neg<N):
                        evids=adjust_evidence_form(sparql_evid)
                        type_evids=get_type_sub_obj(resource)



                        evids_literals=set()
                        for evd in evids:
                            l=get_literals(evd)
                            for ll in l:
                                evids_literals.add(ll)
                        if(subject in evids_literals):
                            evids_literals.remove(subject)
                        if(object in evids_literals):
                            evids_literals.remove(object)



                        if(check_KB_evid_rules(rules,evids,evids_literals,subject,object)):
                            num_neg+=1
                            clm.append(line)
                            print(line)
                            print(num_pos,num_neg)
                            f=open(evid_dir+id+'er_unique.txt','w')
                            for rule in rules:
                                f.write(rule)

                            for evid in evids:
                                f.write(evid)

                            for evid in type_evids:
                                if('owl#' in evid):
                                    evid=evid.replace('owl#','')
                                f.write(evid)


                            f.close()



    print("We found evidence for "+str(num_pos)+" positive relations and "+str(num_neg)+" negative relations.\n")
    f=open(dir+'claims.txt','w')
    for c in clm:
        f.write(c)
    f.close()





def generate_evid_KB_random(rules_file,claims_file,dir,evid_dir,N=100):

    if not os.path.exists(dir):
        os.makedirs(dir)


    if not os.path.exists(evid_dir):
        os.makedirs(evid_dir)



    with open(rules_file,'r', encoding='utf-8', errors='replace') as f:
        rules=f.readlines()

    with open(claims_file,'r', encoding='utf-8', errors='replace') as f:
        lines=f.readlines()


    for i in range(len(lines)):
        if(lines[i].strip().split(',')[-1]=='1' and lines[i+1].strip().split(',')[-1]=='0'):
            limit=i
            break


    pos_limit_id=lines[limit].split(',')[0]
    neg_limit_id=lines[-1].split(',')[0]

    for i in range(0,1):

        pos_claims_idx=[]
        while(len(pos_claims_idx)<N):
            ind=random.sample(range(1,int(pos_limit_id)),1)[0]
            if(ind not in pos_claims_idx): # and is_valid_claim(lines[ind],rules)):
                print(lines[ind])
                pos_claims_idx.append(ind)

        pos_claims_idx=random.sample(range(1,int(pos_limit_id)),N)
        pos_claims=[lines[k] for k in pos_claims_idx]
        neg_claims_idx=[]
        while(len(neg_claims_idx)<N):
            ind=random.sample(range(int(pos_limit_id)+1,int(neg_limit_id)),1)[0]
            if( ind not in neg_claims_idx): # and is_valid_claim(lines[ind],rules)):
                neg_claims_idx.append(ind)
                print(lines[ind])

        neg_claims_idx=random.sample(range(int(pos_limit_id)+1,int(neg_limit_id)),N)
        neg_claims=[lines[k] for k in neg_claims_idx]


        f=open(dir+'claims.txt','w')
        for claim in pos_claims:
            f.write(claim)
        for claim in neg_claims:
            f.write(claim)
        f.close()
        claims=pos_claims+neg_claims
        i=1
        for claim in claims:
            print(i)
            print("################################################")
            print(claim)
            i+=1
            #if(is_ascii(claim)):
            id=claim.split(',')[0]
            resource=[claim.split(',')[1],claim.split(',')[2]]
            label=claim.strip().split(',')[3]


            sparql_evid=get_evidence(resource,rules)
            if(len(sparql_evid)!=0):
                evids=adjust_evidence_form(sparql_evid)
                type_evids=get_type_sub_obj(resource)
                if(evids):
                    f=open(evid_dir+id+'er_unique.txt','w')
                    for rule in rules:
                        f.write(rule)

                    for evid in evids:
                        #print(evid)
                        f.write(evid)

                    for evid in type_evids:
                        if('owl#' in evid):
                            evid=evid.replace('owl#','')
                        f.write(evid)

                    f.close()









