import os, json, time, socket, threading, urllib3, requests, random
from Crypto.Util.Padding import pad, unpad
from Crypto.Cipher import AES
from protobuf_decoder.protobuf_decoder import Parser

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

xK = b'Yg&tc%DEuh6%Zc^8'
xV = b'6oyZDr22E3ychjM%'

ACCOUNTS = [("8001120768", "40c74921aaedcba4fac1")]
TARGET_UID = 18811131543
EMOTE_ID = 909000012
SELF_EMOTE = False

SOCKET_TIMEOUT = 10
JOIN_WAIT = 3.0
AUTH_WAIT = 0.5
DANCE_WAIT = 1.5
EXIT_WAIT = 0.5


def EnV_VaRiAnT(n):
    d = []
    while True:
        b = n & 0x7F
        n >>= 7
        if n:
            b |= 0x80
        d.append(b)
        if not n:
            break
    return bytes(d)


def ProToBuF(Fields):
    p = bytearray()
    for f, v in Fields.items():
        if isinstance(v, bool):
            p.extend(EnV_VaRiAnT((f << 3) | 0))
            p.extend(EnV_VaRiAnT(1 if v else 0))
        elif isinstance(v, int):
            p.extend(EnV_VaRiAnT((f << 3) | 0))
            p.extend(EnV_VaRiAnT(v))
        elif isinstance(v, str):
            d = v.encode()
            p.extend(EnV_VaRiAnT((f << 3) | 2))
            p.extend(EnV_VaRiAnT(len(d)))
            p.extend(d)
        elif isinstance(v, (bytes, bytearray)):
            d = bytes(v)
            p.extend(EnV_VaRiAnT((f << 3) | 2))
            p.extend(EnV_VaRiAnT(len(d)))
            p.extend(d)
        elif isinstance(v, dict):
            d = ProToBuF(v)
            p.extend(EnV_VaRiAnT((f << 3) | 2))
            p.extend(EnV_VaRiAnT(len(d)))
            p.extend(d)
        elif isinstance(v, list):
            for item in v:
                if isinstance(item, dict):
                    d = ProToBuF(item)
                    p.extend(EnV_VaRiAnT((f << 3) | 2))
                    p.extend(EnV_VaRiAnT(len(d)))
                    p.extend(d)
    return bytes(p)


def Read_VaRiAnT(data, pos):
    result = 0
    shift = 0
    while pos < len(data):
        b = data[pos]
        pos += 1
        result |= (b & 0x7F) << shift
        if not (b & 0x80):
            break
        shift += 7
    return result, pos


def Parse_ProToBuF(data):
    fields = {}
    pos = 0
    n = len(data)
    while pos < n:
        try:
            key, pos = Read_VaRiAnT(data, pos)
        except:
            break
        fn = key >> 3
        wt = key & 0x07
        try:
            if wt == 0:
                val, pos = Read_VaRiAnT(data, pos)
            elif wt == 2:
                ln, pos = Read_VaRiAnT(data, pos)
                val = data[pos:pos + ln]
                pos += ln
            elif wt == 5:
                val = data[pos:pos + 4]
                pos += 4
            elif wt == 1:
                val = data[pos:pos + 8]
                pos += 8
            else:
                break
        except:
            break
        fields.setdefault(fn, []).append(val)
    return fields


def Ua():
    return random.choice(['4.0.18P6', '4.0.19P7', '4.0.20P1', '4.1.0P3', '4.1.5P2', '4.2.1P8', '4.2.3P1', '5.0.1B2', '5.0.2P4', '5.1.0P1', '5.2.0B1', '5.2.5P3', '5.3.0B1', '5.3.2P2', '5.4.0P1', '5.4.3B2', '5.5.0P1', '5.5.2P3'])


def EnC_PacKeT(HeX, K, V):
    return AES.new(K, AES.MODE_CBC, V).encrypt(pad(bytes.fromhex(HeX), 16)).hex()


def EnC_Vr(N):
    H = []
    while True:
        BesTo = N & 0x7F
        N >>= 7
        if N:
            BesTo |= 0x80
        H.append(BesTo)
        if not N:
            break
    return bytes(H)


def CrEaTe_VarianT(field_number, value):
    return EnC_Vr((field_number << 3) | 0) + EnC_Vr(value)


def CrEaTe_LenGTh(field_number, value):
    encoded_value = value.encode() if isinstance(value, str) else value
    return EnC_Vr((field_number << 3) | 2) + EnC_Vr(len(encoded_value)) + encoded_value


def CrEaTe_ProTo(fields):
    packet = bytearray()
    for field, value in fields.items():
        if isinstance(value, dict):
            packet.extend(CrEaTe_LenGTh(field, CrEaTe_ProTo(value)))
        elif isinstance(value, int):
            packet.extend(CrEaTe_VarianT(field, value))
        elif isinstance(value, str) or isinstance(value, bytes):
            packet.extend(CrEaTe_LenGTh(field, value))
        elif isinstance(value, list):
            for item in value:
                if isinstance(item, dict):
                    packet.extend(CrEaTe_LenGTh(field, CrEaTe_ProTo(item)))
    return packet


def DecodE_HeX(H):
    F = str(hex(H))[2:]
    return "0" + F if len(F) == 1 else F


def GeneRaTePk(Pk, N, K, V):
    PkEnc = EnC_PacKeT(Pk, K, V)
    _ = DecodE_HeX(int(len(PkEnc) // 2))
    if len(_) == 2:
        HeadEr = N + "000000"
    elif len(_) == 3:
        HeadEr = N + "00000"
    elif len(_) == 4:
        HeadEr = N + "0000"
    elif len(_) == 5:
        HeadEr = N + "000"
    else:
        HeadEr = N + "00000"
    return bytes.fromhex(HeadEr + _ + PkEnc)


def Fix_PackEt(parsed_results):
    result_dict = {}
    for result in parsed_results:
        field_data = {'wire_type': result.wire_type}
        if result.wire_type == "varint":
            field_data['data'] = result.data
        if result.wire_type == "string":
            field_data['data'] = result.data
        if result.wire_type == "bytes":
            field_data['data'] = result.data
        elif result.wire_type == 'length_delimited':
            field_data["data"] = Fix_PackEt(result.data.results)
        result_dict[result.field] = field_data
    return result_dict


def DeCode_PackEt(input_text):
    try:
        parsed_results = Parser().parse(input_text)
        return json.dumps(Fix_PackEt(parsed_results))
    except:
        return None


def decrypt_0515_packet(raw_bytes, key, iv, label=""):
    try:
        head = raw_bytes[:6].hex()
        if not head.startswith("0515"):
            return None
        total_after_header = len(raw_bytes) - 6
        if total_after_header < 2:
            return None
        pkt_len = raw_bytes[4] if total_after_header >= 5 else None
        idx = raw_bytes.find(b'\x05\x15')
        if idx == -1:
            idx = 0
        start = idx + 2
        length_byte = raw_bytes[start] if start < len(raw_bytes) else 0
        payload = raw_bytes[start + 1:start + 1 + length_byte]
        if len(payload) < 16:
            payload = raw_bytes[start + 1:]
        if len(payload) % 16 != 0:
            payload = payload[:len(payload) // 16 * 16]
        dec = AES.new(key, AES.MODE_CBC, iv).decrypt(payload)
        try:
            dec = unpad(dec, 16)
        except:
            pass
        fields = Parse_ProToBuF(dec)
        print(f"\n--- DECRYPT 0515 [{label}] raw={raw_bytes.hex()} ---")
        print(f"decrypted_hex={dec.hex()}")
        for fn, vals in fields.items():
            for v in vals:
                if isinstance(v, bytes):
                    try:
                        txt = v.decode('utf-8')
                        printable = all(32 <= ord(c) < 127 or c in '\n\r\t' for c in txt)
                        if printable and len(txt) < 200:
                            print(f"  field {fn} (str) = {txt!r}")
                            continue
                    except:
                        pass
                    print(f"  field {fn} (bytes[{len(v)}]) = {v.hex()[:120]}")
                else:
                    print(f"  field {fn} = {v}")
        return fields
    except Exception as e:
        print(f"--- DECRYPT 0515 [{label}] FAILED: {e} raw={raw_bytes.hex()[:120]}")
        return None


def Join_Team(team_code, key, iv):
    fields = {1: bytes.fromhex("01090a0b121619201d2729"), 2: 40, 3: bytes.fromhex("01090a0b121619201d2729"), 4: "w\\Z]", 6: 12, 7: bytes.fromhex("01090a0b121619201d2729"), 8: "1.132.9", 9: 6, 10: 2, 11: bytes.fromhex("01090a0b121619201d2729")}
    f = {1: 4, 2: {4: bytes.fromhex("01090a0b121619201d2729"), 5: str(team_code), 6: 6, 8: 1, 9: fields, 11: {1: "IDC1", 2: 99, 3: "ME"}, 13: "ar", 16: bytes.fromhex("374f521955"), 20: [{1: 3, 2: 360}, {1: 4, 2: 391}, {1: 5, 2: 156}, {1: 29, 2: 204}, {1: 22, 2: 118}, {1: 14, 2: 139}, {1: 21}], 27: {1: 2, 2: 4}}}
    return GeneRaTePk(CrEaTe_ProTo(f).hex(), "0515", key, iv)


def Emote_k(target_uid, emote_id, bot_uid, key, iv):
    fields = {
        1: 21,
        2: {
            1: int(bot_uid),
            2: 909000001,
            5: {
                1: int(target_uid),
                3: int(emote_id),
            }
        }
    }
    return GeneRaTePk(CrEaTe_ProTo(fields).hex(), '0515', key, iv)


def ExiT(key, iv):
    fields = {1: 7, 2: {1: 0}}
    return GeneRaTePk(str(CrEaTe_ProTo(fields).hex()), '0515', key, iv)


def AutH_Chat(chat_type, owner_uid, chat_code, key, iv):
    fields = {1: chat_type, 2: {1: int(owner_uid), 3: "en", 4: str(chat_code)}}
    return GeneRaTePk(CrEaTe_ProTo(fields).hex(), '1215', key, iv)


def PyL(access_token, open_id):
    P = {}
    P[3] = time.strftime("%Y-%m-%d %H:%M:%S"); P[4] = "free fire"; P[5] = 1; P[7] = "1.132.9"
    P[8] = "Android OS 14 / API-34 (UP1A.231005.007/V816.0.15.0.UNQMIXM)"
    P[9] = "Handheld"; P[10] = "Grameenphone"; P[11] = "CarrierDataNetwork"
    P[12] = 1666; P[13] = 750; P[14] = "352"; P[15] = "ARM64 FP ASIMD AES | 2400 | 8"
    P[16] = 5563; P[17] = "Mali-G57 MC2"
    P[18] = "OpenGL ES 3.2 v1.r32p1-01eac0.0a0b917d9265b4c01be9925306306139"
    P[19] = "Google|9cc73f7a-91f6-40f6-87ec-5b67e597eb8c"; P[20] = "59.152.5.188"
    P[21] = "en"; P[22] = open_id; P[23] = "8"; P[24] = "Handheld"
    P[25] = "Xiaomi 2312DRAABI"; P[26] = "BD"; P[29] = access_token; P[30] = 1
    P[41] = "Grameenphone"; P[42] = "Cellular"
    P[57] = "7428b253defc164018c604a1ebbfebdf"
    P[60] = 109685; P[61] = 58294; P[62] = 797; P[63] = 18000; P[64] = 58818; P[65] = 109685
    P[66] = 58818; P[67] = 109685; P[73] = 2
    P[74] = "/data/app/~~cqQgpdMykLQEM3odipXatw==/com.dts.freefireth-G6e5yOt1dtuXG5Ambhj18g==/lib/arm64"
    P[76] = 1
    P[77] = "b8e0cd5e295eee42f5860d3c86e483dd|/data/app/~~cqQgpdMykLQEM3odipXatw==/com.dts.freefireth-G6e5yOt1dtuXG5Ambhj18g==/base.apk"
    P[78] = 3; P[79] = 2; P[81] = "64"; P[83] = "2019121229"; P[85] = 3; P[86] = "OpenGLES2"
    P[87] = 4095; P[88] = 8
    P[89] = b"FwQVTgUPX1UaUllDDwcWCRBpWAUOUgsvA1snWlBaO1kFYg=="
    P[90] = "Dhaka"; P[91] = "C"; P[92] = 8043; P[93] = "android"
    P[94] = "KqsHT4XbSZhqerDNUhjbS3DxG/4+I62zQU2tZFJN91kBUICAlZ5yujshLKvjlk/KiShfKfis8EeB1PMhFHIodWPncZC4fCHYF3TcTwNj95aWY/S3"
    P[95] = 111207; P[96] = '{"cur_rate":[60,90,120],"support_etc2":false}'
    P[97] = 1; P[98] = 1; P[99] = "4"; P[100] = "4"; P[102] = "GQ]        e"; P[103] = 1
    P[104] = 45174; P[105] = 1
    P[106] = "https://dl-bs.ggpolarbear.com/live/ABHotUpdates/|https://core-bs.ggpolarbear.com/live/ABHotUpdates/|a4332cb1c1a84e51dd77441e4856ed5a"
    P[107] = "1.9393e7b8e53e8aeb"
    return AES.new(xK, AES.MODE_CBC, xV).encrypt(pad(ProToBuF(P), 16))


def Strip_MajorLogin_Prefix(body):
    if len(body) <= 64:
        return body
    try:
        if 8 in Parse_ProToBuF(body):
            return body
    except:
        pass
    try:
        if 8 in Parse_ProToBuF(body[64:]):
            return body[64:]
    except:
        pass
    return body


def GeT_AccEss(uid, password):
    url = "https://100067.connect.garena.com/api/v2/oauth/guest/token:grant"
    headers = {"User-Agent": Ua(), "Content-Type": "application/json; charset=utf-8"}
    R = requests.post(url, headers=headers, json={"client_id": 100067, "client_secret": "2ee44819e9b4598845141067b281621874d0d5d7af9d8f7e00c1e54715b7d1e3", "client_type": 2, "device_id": "", "password": password, "response_type": "token", "uid": int(uid)}, verify=False, timeout=15)
    print(f"[{uid}] Get access => {R.status_code}")
    if R.status_code not in (200, 201):
        return None
    try:
        J = R.json()
    except:
        return None
    if J.get("code") != 0:
        return None
    d = J.get("data", {})
    return {"access_token": d.get("access_token"), "open_id": d.get("open_id")}


def MajorLogin(Payload):
    url = "https://loginbp.ppmainecoonghj.com/MajorLogin"
    headers = {"User-Agent": "UnityPlayer/2018.4.12f1 (UnityWebRequest/1.0, libcurl/8.5.0-DEV)", "Accept": "*/*", "Accept-Encoding": "deflate, gzip", "X-GA-SV": str(int(time.time())), "Authorization": "Bearer ", "X-GA": "v1 1", "ReleaseVersion": "OB55", "Content-Type": "application/x-www-form-urlencoded", "X-Unity-Version": "2018.4.12f1"}
    R = requests.post(url, headers=headers, data=Payload, verify=False, timeout=15)
    print(f"MajorLogin => {R.status_code}")
    return R.content if R.status_code in (200, 201) and R.content else None


def GeTLoginDaTa(client_url, payload, jwt):
    url = f"{client_url}/GetLoginData"
    headers = {"User-Agent": "UnityPlayer/2018.4.12f1 (UnityWebRequest/1.0, libcurl/8.5.0-DEV)", "Accept": "*/*", "Accept-Encoding": "deflate, gzip", "X-GA-SV": str(int(time.time())), "Authorization": f"Bearer {jwt}", "X-GA": "v1 1", "ReleaseVersion": "OB55", "Content-Type": "application/x-www-form-urlencoded", "X-Unity-Version": "2018.4.12f1"}
    R = requests.post(url, headers=headers, data=payload, verify=False, timeout=15)
    print(f"GetLoginData => {R.status_code}")
    return R.content if R.status_code == 200 and R.content else None


def _gv(fields, n):
    v = fields.get(n)
    if v is None:
        return None
    if isinstance(v, list):
        v = v[0]
    return v


def ExtractMajorLogin(ml_resp):
    body = Strip_MajorLogin_Prefix(ml_resp)
    f = Parse_ProToBuF(body)
    jwt_b = _gv(f, 8)
    url_b = _gv(f, 10)
    ts_v = _gv(f, 21)
    key_b = _gv(f, 22)
    iv_b = _gv(f, 23)
    acct_v = _gv(f, 1)
    jwt = None
    if isinstance(jwt_b, bytes):
        try:
            jwt = jwt_b.decode("utf-8")
        except:
            jwt = jwt_b.decode("utf-8", errors="ignore")
    elif isinstance(jwt_b, str):
        jwt = jwt_b
    url = None
    if isinstance(url_b, bytes):
        try:
            url = url_b.decode("utf-8")
        except:
            url = None
    elif isinstance(url_b, str):
        url = url_b
    ts = ts_v if isinstance(ts_v, int) else None
    acct = acct_v if isinstance(acct_v, int) else None
    if not jwt or not isinstance(key_b, bytes) or not isinstance(iv_b, bytes):
        print(f"[ML] missing fields")
        return None
    return {"jwt": jwt, "url": url, "ts": ts, "key": key_b, "iv": iv_b, "account_id": acct}


def BuildAuthToken(uid, jwt_str, ts, key, iv, mode="online"):
    ah = f"{int(uid):x}"
    if len(ah) > 16:
        raise ValueError("uid hex too long")
    ah = ah.zfill(16)
    enc = AES.new(key, AES.MODE_CBC, iv).encrypt(pad(jwt_str.encode(), 16)).hex()
    th = f"{int(ts):x}"
    if len(th) % 2:
        th = "0" + th
    tsz = f"{len(enc)//2:02x}"
    pad_ = "00000" if mode == "chat" else "0000000000000"
    return f"9015{ah}{th}{pad_}{tsz}{enc}"


def _TuneSock(s):
    s.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)
    try:
        s.setsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPIDLE, 30)
        s.setsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPINTVL, 10)
        s.setsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPCNT, 3)
    except Exception:
        pass


def login_account(acc_uid, acc_pass):
    td = GeT_AccEss(acc_uid, acc_pass)
    if not td:
        return None
    access_token = td["access_token"]
    open_id = td["open_id"]
    if not access_token or not open_id:
        return None
    login_payload = PyL(access_token, open_id)
    ml = MajorLogin(login_payload)
    if not ml:
        return None
    ad = ExtractMajorLogin(ml)
    if not ad:
        print(f"[{acc_uid}] MajorLogin parse failed")
        return None
    jwt = ad["jwt"]
    ts = ad["ts"]
    key = ad["key"]
    iv = ad["iv"]
    url = ad["url"] or "https://clientbp.ppmainecoonghj.com"
    if not url.startswith(("http://", "https://")):
        url = "https://" + url
    account_id = ad["account_id"]
    print(f"[{acc_uid}] JWT len={len(jwt)} | ts={ts} | acct={account_id}")
    ld = GeTLoginDaTa(url, login_payload, jwt)
    if not ld:
        return None
    gl = Parse_ProToBuF(ld)

    def gv(n):
        v = gl.get(n)
        if v is None:
            return None
        if isinstance(v, list):
            v = v[0]
        return v

    def gs(n):
        v = gv(n)
        return v.decode() if isinstance(v, bytes) else v

    def gi(n):
        v = gv(n)
        return int(v) if isinstance(v, int) else None

    player_name = gs(4) or ""
    func_addr = gs(14)
    if not func_addr:
        print(f"[{acc_uid}] missing ip:port")
        return None
    ip, port = func_addr.split(":")
    if not account_id:
        account_id = gi(1) or gi(5) or 0
    print(f"[{acc_uid}] BoT Is OnLiNe | {player_name} | UID: {account_id}")
    return {
        "uid": account_id,
        "jwt": jwt, "ts": ts, "key": key, "iv": iv,
        "ip": ip, "port": port,
        "name": player_name, "token": access_token,
    }


def wait_response(s, seconds, key=None, iv=None, label=""):
    buf = b""
    end = time.time() + seconds
    s.settimeout(0.5)
    while time.time() < end:
        try:
            chunk = s.recv(65536)
            if not chunk:
                break
            buf += chunk
            if key and iv:
                try:
                    idx = 0
                    while idx < len(chunk):
                        pos = chunk.find(b'\x05\x15', idx)
                        if pos == -1:
                            break
                        sub = chunk[pos:]
                        decrypt_0515_packet(sub, key, iv, label=label)
                        idx = pos + 2
                except Exception as e:
                    print(f"[decrypt err] {e}")
        except socket.timeout:
            continue
        except Exception:
            break
    return buf


def extract_team_data(resp):
    owner_uid = None
    chat_code = None
    squad_code = None
    hex_str = resp.hex()
    if hex_str.startswith('0500') and len(hex_str) > 100:
        js = DeCode_PackEt(hex_str[10:])
        if js:
            try:
                packet = json.loads(js)
                owner_uid = packet.get('5', {}).get('data', {}).get('1', {}).get('data')
                chat_code = packet.get('5', {}).get('data', {}).get('14', {}).get('data')
                squad_code = packet.get('5', {}).get('data', {}).get('31', {}).get('data')
            except:
                pass
    return owner_uid, chat_code, squad_code


def session_loop(sess):
    uid = sess["uid"]
    host = sess["ip"]
    port = int(sess["port"])
    key = sess["key"]
    iv = sess["iv"]
    jwt = sess["jwt"]
    ts = sess["ts"]

    s = None
    try:
        s = socket.create_connection((host, port), timeout=15)
        s.settimeout(SOCKET_TIMEOUT)
        _TuneSock(s)
        auth_hex = BuildAuthToken(uid, jwt, ts, key, iv, mode="online")
        s.sendall(bytes.fromhex(auth_hex))
        print(f"[{uid}] connected to {host}:{port}")
        wait_response(s, 1.0, key, iv, label="after-auth")
    except Exception as e:
        print(f"[{uid}] connect err: {e}")
        return

    round_num = 0
    while True:
        try:
            team_code = input(f"\n[{uid}] Enter Team Code (or 'exit') => ").strip()
        except (EOFError, KeyboardInterrupt):
            print(f"\n[{uid}] terminating")
            break
        if not team_code or team_code.lower() == "exit":
            print(f"[{uid}] terminating by user")
            break

        round_num += 1
        print(f"\n[{uid}] === round {round_num} | team={team_code} ===")

        try:
            s.sendall(Join_Team(team_code, key, iv))
            print(f"[{uid}] JOIN sent")
            resp = wait_response(s, JOIN_WAIT, key, iv, label="join")
            print(f"[{uid}] JOIN resp len={len(resp)}")
        except Exception as e:
            print(f"[{uid}] join err: {e}")
            break

        owner_uid, chat_code, squad_code = extract_team_data(resp)
        print(f"[{uid}] extracted owner={owner_uid} chat={chat_code} squad_len={len(str(squad_code)) if squad_code else 0}")

        if owner_uid and chat_code:
            try:
                s.sendall(AutH_Chat(3, owner_uid, chat_code, key, iv))
                print(f"[{uid}] AUTH_CHAT sent")
                wait_response(s, AUTH_WAIT, key, iv, label="auth-chat")
            except Exception as e:
                print(f"[{uid}] auth_chat err: {e}")

        actual_target = uid if SELF_EMOTE else TARGET_UID
        print(f"[{uid}] dancing target={actual_target} emote={EMOTE_ID}")

        try:
            s.sendall(Emote_k(actual_target, EMOTE_ID, uid, key, iv))
            print(f"[{uid}] DANCE sent")
            time.sleep(0.3)
            s.sendall(Emote_k(actual_target, EMOTE_ID, uid, key, iv))
            print(f"[{uid}] DANCE sent again")
            dresp = wait_response(s, DANCE_WAIT, key, iv, label="dance")
            print(f"[{uid}] DANCE resp len={len(dresp)}")
        except Exception as e:
            print(f"[{uid}] dance err: {e}")
            break

        try:
            s.sendall(ExiT(key, iv))
            print(f"[{uid}] EXIT sent")
            wait_response(s, EXIT_WAIT, key, iv, label="exit")
        except Exception as e:
            print(f"[{uid}] exit err: {e}")
            break

        print(f"[{uid}] round {round_num} done, connection kept alive")

    try:
        s.close()
    except:
        pass
    print(f"[{uid}] socket closed")


def main():
    sessions = []
    for acc_uid, acc_pass in ACCOUNTS:
        try:
            res = login_account(acc_uid, acc_pass)
            if res:
                sessions.append(res)
        except Exception as e:
            print(f"[{acc_uid}] login err: {e}")

    if not sessions:
        print("No sessions logged in. Exiting.")
        return

    print(f"\n==== {len(sessions)} accounts ready ====\n")

    threads = []
    for s in sessions:
        t = threading.Thread(target=session_loop, args=(s,), daemon=False)
        t.start()
        threads.append(t)

    try:
        for t in threads:
            t.join()
    except KeyboardInterrupt:
        print("\nInterrupted by user")

    print("ALL DONE")


if __name__ == "__main__":
    main()