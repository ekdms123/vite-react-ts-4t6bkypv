import { useState } from 'react'
import { createRoot } from 'react-dom/client'
import './styles/app.css'

/**
 * 디자인 미리보기. 실제 앱과 같은 CSS·같은 마크업을 쓰되 데이터만 가짜다.
 * Supabase를 붙이기 전에 모양을 확정하려고 둔다.
 */

const TABS = ['홈', '오늘', '달력', '다이어리', '사진첩', '사진한장', '가계부', '챌린지', '쥬크박스', '보관함', '방명록']
const won = (n: number) => n.toLocaleString('ko-KR') + '원'

function Home() {
  return (
    <div className="home">
      <section className="block capture">
        <div className="news-title">지금 떠오른 것</div>
        <textarea rows={2} defaultValue="" placeholder="아무거나. 분류는 나중에." />
        <div className="capture-foot">
          <span className="k">⌘/Ctrl + Enter</span>
          <button className="btn">던지기</button>
        </div>
      </section>

      <section className="block">
        <div className="news-title">오늘</div>
        <ul className="checklist">
          <li><button className="tick" aria-label="다 했음으로 표시" /><span className="what">과제 개요 1장 쓰기</span><span className="dday now">오늘</span></li>
          <li><button className="tick" aria-label="다 했음으로 표시" /><span className="what">병원 예약 전화</span><span className="dday past">2일 지남</span></li>
          <li><button className="tick" aria-label="다 했음으로 표시" /><span className="what">빨래 돌리기</span></li>
        </ul>
        <div className="k soft">4개는 접어뒀다.</div>
      </section>

      <section className="block">
        <div className="news-title">곧 마감</div>
        <ul className="due-list">
          <li><span className="chip">오늘</span><span className="what">교양 레포트 제출</span><b>9/22</b></li>
          <li><span className="chip">오늘</span><span className="what">동아리 회비</span><b>9/23</b></li>
        </ul>
      </section>

      <section className="block">
        <div className="news-title">Updated news</div>
        <div className="news-row"><span className="chip">다이어리</span><span className="what">오늘 커피 두 잔이나 마심</span><span className="when">9/20</span></div>
        <div className="news-row"><span className="chip">사진첩</span><span className="what">한강 노을</span><span className="when">9/19</span></div>
        <div className="news-row"><span className="chip">가계부</span><span className="what">점심 김밥</span><span className="when">9/19</span></div>
        <div className="counts">
          {[['오늘', 7], ['달력', 12], ['다이어리', 31], ['사진첩', 64], ['가계부', 28], ['챌린지', 3], ['쥬크박스', 9], ['보관함', 15]].map(([k, v]) => (
            <button key={k as string} className="count-cell">
              <span className="k">{k}</span><span className="v">{v}</span>
            </button>
          ))}
        </div>
      </section>
    </div>
  )
}

function Todo() {
  const G: [string,string,string,[string,string|null][]][] = [
    ['past','지났다','오늘로 당기거나 지워도 된다',[['병원 예약 전화','2일 지남'],['책 반납','5일 지남']]],
    ['today','오늘','',[['교양 레포트 제출','오늘'],['빨래 돌리기',null],['약 먹기',null]]],
    ['week','이번 주','',[['동아리 회비 보내기','D-3'],['장보기','D-4'],['미용실','D-6']]],
    ['later','나중에','',[['여권 갱신','D-24']]],
    ['someday','언젠가','날짜를 안 정한 것들',[['책장 정리',null],['사진 백업',null]]],
  ]
  return (
    <div>
      <div className="sec-title">오늘<span style={{float:'right',fontWeight:400,color:'#636363'}}>11개 남음</span></div>
      <div className="quick-add">
        <input type="text" placeholder="할 일 한 줄" />
        <input type="date" style={{width:126}} aria-label="마감 날짜" />
        <button className="btn">담기</button>
      </div>
      {G.map(([key,label,hint,items]) => (
        <details key={key} className="bucket" open={key!=='later'&&key!=='someday'} data-tone={key}>
          <summary>
            <span className="b-label">{label}</span>
            <span className="b-count">{items.length}</span>
            {hint && <span className="b-hint">{hint}</span>}
          </summary>
          <ul className="checklist">
            {items.map(([t,d]) => (
              <li key={t}>
                <button className="tick" aria-label="다 했음으로 표시" />
                <span className="what">{t}</span>
                {key==='past' && <button className="crumb pull-today">오늘로</button>}
                {d && <span className={`dday ${d==='오늘'?'now':d.includes('지남')?'past':'soon'}`}>{d}</span>}
                <button className="x" aria-label="지우기">×</button>
              </li>
            ))}
          </ul>
        </details>
      ))}
      <div style={{marginTop:14}}><button className="fold">▸ 끝낸 것 12</button></div>
    </div>
  )
}

function Cal() {
  const WEEK = ['일', '월', '화', '수', '목', '금', '토']
  const marks: Record<number, number> = { 3: 1, 8: 2, 12: 1, 15: 3, 20: 2, 22: 1, 27: 1 }
  return (
    <div>
      <div className="sec-title cal-head">
        <button className="nav" aria-label="지난달">‹</button><span>2026년 9월</span><button className="nav" aria-label="다음달">›</button>
      </div>
      <div className="cal-grid">
        {WEEK.map((w, i) => <div key={w} className="cal-wd" data-sun={i === 0} data-sat={i === 6}>{w}</div>)}
        {Array.from({ length: 42 }, (_, i) => {
          const day = i - 1
          const inMonth = day >= 1 && day <= 30
          return (
            <button key={i} className="cal-day" data-dim={!inMonth}
                    aria-label={inMonth ? `9월 ${day}일` : '이번 달 아님'}
                    data-today={day === 20} data-picked={day === 20}>
              <span>{inMonth ? day : ''}</span>
              {inMonth && marks[day] ? <i className="dot" data-n={marks[day]} /> : null}
            </button>
          )
        })}
      </div>
      <div className="cal-day-panel">
        <div className="k">2026.09.20</div>
        <ul className="day-list">
          <li><time>10:00</time><span className="what">팀플 회의</span><button className="x" aria-label="지우기">×</button></li>
          <li><time>19:30</time><span className="what">엄마 생신 저녁</span><button className="x" aria-label="지우기">×</button></li>
        </ul>
        <div className="quick-add">
          <input type="time" style={{ width: 96 }} aria-label="시간" /><input type="text" placeholder="무슨 일" />
          <button className="btn">담기</button>
        </div>
      </div>
    </div>
  )
}

function Ch() {
  const mk = (on: number[]) => Array.from({ length: 35 }, (_, i) => on.includes(i))
  const rows: [string, number, number, boolean[]][] = [
    ['물 2L 마시기', 6, 24, mk([1,2,4,5,7,8,9,11,12,14,16,17,19,20,21,23,25,26,28,29,30,31,32,33])],
    ['자기 전 스트레칭', 0, 11, mk([2,5,9,13,15,18,21,24,26,29,30])],
  ]
  return (
    <div>
      <div className="sec-title">챌린지</div>
      <div className="quick-add">
        <input type="text" placeholder="새 챌린지 이름 (예: 물 마시기)" />
        <button className="btn">시작</button>
      </div>
      {rows.map(([label, streak, total, cells]) => (
        <div key={label} className="challenge">
          <div className="ch-head">
            <b>{label}</b>
            <span className="k">연속 {streak}일 · 누적 {total}일</span>
            <button className={`btn ${streak > 0 ? 'ghost' : ''}`}>{streak > 0 ? '오늘 했음' : '오늘 하기'}</button>
          </div>
          <div className="grass">{cells.map((on, i) => <i key={i} data-on={on} />)}</div>
          {streak === 0 && <div className="k soft">끊겼어도 {total}일은 그대로 남아 있다.</div>}
        </div>
      ))}
    </div>
  )
}

function Guest() {
  return (
    <div>
      <div className="sec-title">방명록 <span style={{ color: '#636363', fontWeight: 400 }}>3</span></div>
      <div style={{ display: 'grid', gap: 6, marginBottom: 14 }}>
        <textarea rows={3} placeholder="한마디 남기고 가기" />
        <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
          <label className="tiny"><input type="checkbox" style={{ width: 'auto' }} />비밀글</label>
          <button className="btn" style={{ marginLeft: 'auto' }}>남기기</button>
        </div>
      </div>
      {[['지민', '잘 지내지? 나 일촌 신청했어ㅎㅎ', false],
        ['수연', '어제 고마웠어!!', true],
        ['하람', '홈피 꾸민 거 예쁘다', false]].map(([who, what, secret]) => (
        <div key={who as string} style={{ display: 'flex', gap: 8, padding: '9px 0', borderBottom: '1px solid var(--line)' }}>
          <div style={{ flex: '0 0 32px', height: 32, borderRadius: 4, background: '#eef3f5', border: '1px solid var(--line)' }} />
          <div style={{ flex: 1, minWidth: 0 }}>
            <div style={{ fontSize: 11 }}>
              <b style={{ color: 'var(--title)' }}>{who as string}</b>
              <span style={{ color: 'var(--ink-soft)', marginLeft: 6 }}>9/19</span>
              {secret ? <span className="chip" style={{ marginLeft: 6 }}>비밀</span> : null}
            </div>
            <div style={{ lineHeight: 1.7 }}>{what as string}</div>
          </div>
        </div>
      ))}
    </div>
  )
}

function Dia() {
  const days: [number, string, string, string, string][] = [
    [20, '9월', '금', '🌷 행복', '오늘 과제 겨우 냈다. 끝나고 먹은 아이스크림이 제일 맛있었음.\n내일은 좀 쉬어야지.'],
    [19, '9월', '목', '☁️ 그냥그럼', '커피 두 잔이나 마셨다. 잠이 안 온다.'],
    [17, '9월', '화', '🌟 뿌듯', '3주 미루던 병원 예약 드디어 했다.'],
  ]
  return (
    <div>
      <div className="sec-title">다이어리<span style={{ float: 'right', fontWeight: 400, color: '#636363' }}>31일</span></div>
      <button className="diary-open">✎ 오늘 쓰기</button>
      <nav className="month-jump" aria-label="달로 건너뛰기">
        {[['09',31],['08',26],['07',19],['06',24],['05',12]].map(([m,n]) => (
          <a key={m as string} href="#m">{m}월<i>{n}</i></a>
        ))}
      </nav>
      <h3 className="month-rule"><span>2026년 9월</span><i>31편</i></h3>
      <div className="diary-list">
        {days.map(([d, m, w, mood, body]) => (
          <article key={d} className="diary-day">
            <div className="tearoff"><b>{d}</b><span>{m}</span><em>{w}</em></div>
            <div className="diary-body">
              <div className="diary-meta">
                <span className="mood-tag">{mood}</span>
                <span className="wx">{d === 19 ? '🌧' : '☀️'}</span>
                <button className="x" style={{ marginLeft: 'auto' }}>×</button>
              </div>
              <p>{body}</p>
              {d === 20 && (
                <div className="diary-pics">
                  <div style={{ width: 132, height: 88, borderRadius: 5, background: '#f3c9d4', border: '1px solid var(--line)' }} />
                </div>
              )}
            </div>
          </article>
        ))}
      </div>
    </div>
  )
}

function Juke() {
  const songs = ['좋은 날', 'Through the Night', '밤편지', '너의 의미', 'Spring Day']
  return (
    <div>
      <div className="sec-title">쥬크박스<span style={{ float: 'right', fontWeight: 400, color: '#636363' }}>5곡</span></div>
      <div className="deck">
        <div className="deck-screen"><div style={{ width: '100%', aspectRatio: '16/9', background: '#111' }} /></div>
        <div className="deck-label"><span className="reel" /> <b>좋은 날</b> <span className="reel" /></div>
      </div>
      <div className="quick-add">
        <input type="text" placeholder="유튜브 주소 붙여넣기" />
        <input type="text" placeholder="곡 이름" style={{ maxWidth: 120 }} />
        <button className="btn">담기</button>
      </div>
      <ol className="tracklist">
        {songs.map((s, i) => (
          <li key={s} data-on={i === 0}>
            <span className="no">{String(i + 1).padStart(2, '0')}</span>
            <button className="what">{s}</button>
            {i === 0 && <span className="eq"><i /><i /><i /></span>}
            <button className="x" aria-label="지우기">×</button>
          </li>
        ))}
      </ol>
    </div>
  )
}

function Box() {
  const notes = ['그 영화 제목 뭐였지\n— 주인공이 시계 고치던 거',
    '엄마 생신 선물 알아보기', '다음 학기 시간표 겹치는지 확인',
    '치과 예약 — 오른쪽 어금니', '읽다 만 책 3권 정리']
  return (
    <div>
      <div className="sec-title">보관함<span style={{ float: 'right', fontWeight: 400, color: '#636363' }}>5장</span></div>
      <div className="quick-add">
        <input type="text" placeholder="아무거나 던져두기" />
        <button className="btn">붙이기</button>
      </div>
      <div className="stickies">
        {notes.map((n, i) => (
          <div key={n} className="sticky" data-hue={i % 4}>
            <p>{n}</p>
            <div className="sticky-foot">
              <span className="when">9/{20 - i}</span>
              <select defaultValue="" aria-label="다른 탭으로 옮기기"><option value="">어디로 →</option></select>
              <button className="x" aria-label="지우기">×</button>
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}


function Money2() {
  const cats: [string, number][] = [['식비',182000],['카페',63000],['교통',44000],['쇼핑',39000],['구독',21500]]
  const spent = 349500, prev = 412000, income = 800000, planned = 450000
  const daily = [0,12000,0,0,38000,4500,0,22000,9800,0,0,61000,3200,0,0,18000,0,7400,9300,44000,0,0,0,0,0,0,0,0,0,0]
  const peak = Math.max(...daily)
  const pct = Math.round((spent/planned)*100)
  return (
    <div>
      <div className="sec-title cal-head"><button className="nav" aria-label="지난달">‹</button><span>2026년 9월</span><button className="nav" aria-label="다음달">›</button></div>
      <div className="money-grid">
        <div className="mcell out"><span className="k">썼다</span><b>{won(spent)}</b>
          <em data-up={false}>지난달보다 {won(prev-spent)} 덜</em></div>
        <div className="mcell in"><span className="k">들어왔다</span><b>{won(income)}</b></div>
        <div className="mcell net"><span className="k">남았다</span><b>{won(income-spent)}</b></div>
      </div>
      <div className="budget">
        <div className="bar"><i style={{width:`${pct}%`}} /></div>
        <div className="k">예산 {won(planned)} 중 {pct}% · {won(planned-spent)} 남음</div>
      </div>
      <div className="spark">
        {daily.map((v,i) => <i key={i} style={{height:`${Math.max(2,(v/peak)*100)}%`}} data-has={v>0} />)}
      </div>
      <div className="quick-add money">
        <div className="io"><button data-on>지출</button><button>수입</button></div>
        <input type="text" placeholder="금액" style={{width:88}} />
        <select style={{width:84}} aria-label="분류"><option>식비</option></select>
        <input type="text" placeholder="뭐에 썼나 (생략 가능)" />
        <label className="tiny"><input type="checkbox" style={{width:'auto'}} aria-label="예산으로 담기" />예산</label>
        <button className="btn">담기</button>
      </div>
      <div className="biggest">이번 달 제일 큰 지출 — <b>겨울 코트</b> {won(61000)}</div>
      <div className="cat-rows">
        {cats.map(([k,v]) => (
          <div key={k} className="cat-row">
            <span className="chip">{k}</span>
            <i style={{width:`${Math.round((v/spent)*100)}%`}} />
            <b>{won(v)}</b><em className="pctl">{Math.round((v/spent)*100)}%</em>
          </div>
        ))}
      </div>
      <div className="day-group">
        <div className="day-rule"><span>25일</span><i>+{won(800000)}</i></div>
        <ul className="ledger-list">
          <li data-income><span className="chip">월급</span><span className="what">9월 월급</span><b>+{won(800000)}</b><span className="when">25일</span><button className="x" aria-label="지우기">×</button></li>
        </ul>
      </div>
      <div className="day-group">
        <div className="day-rule"><span>19일</span><i>−{won(9300)}</i></div>
        <ul className="ledger-list">
          <li><span className="chip">식비</span><span className="what">점심 김밥</span><b>−{won(4500)}</b><span className="when">19일</span><button className="x" aria-label="지우기">×</button></li>
          <li><span className="chip">카페</span><span className="what">아메리카노</span><b>−{won(4800)}</b><span className="when">19일</span><button className="x" aria-label="지우기">×</button></li>
        </ul>
      </div>
    </div>
  )
}

function Albums() {
  const al: [string,string,number][] = [['#f3c9d4','여행',24],['#cfe0f5','일상',61],['#d9eede','카페',13],['#e0d6f2','우리 고양이',88]]
  return (
    <div>
      <div className="sec-title">사진첩<span style={{float:'right',fontWeight:400,color:'#636363'}}>앨범 4</span></div>
      <button className="photo-drop">＋ 새 앨범</button>
      <div className="albums">
        {al.map(([c,n,k]) => (
          <button key={n} className="album">
            <div className="album-cover"><div style={{width:'100%',height:'100%',background:c,borderRadius:3}} /><i className="album-back" /></div>
            <div className="album-name">{n}</div><div className="album-count">{k}장</div>
          </button>
        ))}
      </div>
    </div>
  )
}

function PhotoOne() {
  return (
    <div className="photopage" style={{background:'#fff6e5'}}>
      <div className="pp-bar"><button className="crumb">‹ 앨범으로</button><button className="crumb">꾸미기</button></div>
      <div className="pp-tools">
        <div className="pp-row"><span>배경</span>
          {['#ffffff','#fff6e5','#ffeef2','#eaf4f8','#eef7ee','#f3eefa','#2b2b30'].map(c =>
            <button key={c} className="swatch" style={{background:c}} data-on={c==='#fff6e5'} aria-label={`배경 ${c}`} />)}
        </div>
        <div className="pp-row"><span>테두리</span>
          {['폴라로이드','필름','그냥','레이스'].map((f,i) =>
            <button key={f} className="pill" data-on={i===0}>{f}</button>)}
        </div>
      </div>
      <figure className="pp-photo frame-polaroid">
        <div style={{width:'100%',aspectRatio:'4/3',background:'#f3c9d4'}} />
        <figcaption>한강 노을</figcaption>
      </figure>
      <p className="pp-note">이날 바람이 진짜 좋았다.{'\n'}또 가고 싶다.</p>
      <div className="pp-comments">
        <div className="news-title">댓글 2</div>
        {[['동생','나도 데려가지ㅠㅠ'],['수연','사진 진짜 잘 찍었다']].map(([w,b]) => (
          <div key={w} className="pp-c">
            <div className="ava" /><div className="pp-c-body"><b>{w}</b><span className="when">9/19</span><p>{b}</p></div>
            <button className="x" aria-label="지우기">×</button>
          </div>
        ))}
        <div className="quick-add" style={{marginTop:10}}>
          <input type="text" placeholder="한마디" /><button className="btn">달기</button>
        </div>
      </div>
    </div>
  )
}

const PANES: Record<string, () => JSX.Element> = {
  홈: Home, 오늘: Todo, 달력: Cal, 챌린지: Ch, 방명록: Guest,
  다이어리: Dia, 사진첩: Albums, 쥬크박스: Juke, 보관함: Box,
  가계부: Money2, 사진한장: PhotoOne,
}

function Preview() {
  const [tab, setTab] = useState('홈')
  const [skin, setSkin] = useState('sky')
  const Pane = PANES[tab] ?? (() => <div className="empty-note">여기엔 아무거나 던져도 된다.</div>)
  document.documentElement.dataset.skin = skin

  return (
    <div className="stage">
      <div className="binder-wrap">
        <div className="skins" style={{ paddingBottom: 10, justifyContent: 'center' }}>
          {['sky', 'pink', 'mint', 'night'].map(s => (
            <button key={s} data-skin={s} data-on={skin === s} onClick={() => setSkin(s)}>
              {{ sky: '하늘', pink: '핑크', mint: '민트', night: '밤' }[s]}
            </button>
          ))}
        </div>

        <div className="binder">
          <div className="spread">
            <aside aria-label="프로필" className="page-left">
              <div className="counter">TODAY <b>12</b> | TOTAL <span className="total">3,481</span></div>
              <div className="left-card">
                <div className="minimi"><span className="empty">프사<br />없음</span>
                  <button className="upload">사진 바꾸기</button></div>
                <div className="left-head-text">
                  <div className="home-name">다은님의 미니홈피</div>
                  <div className="home-tagline">오늘도 어떻게든</div>
                  <div className="mood-row"><span className="label">TODAY IS..</span>
                    <select defaultValue="그냥그럼" aria-label="오늘 기분"><option>그냥그럼</option></select></div>
                  <div className="energy">
                    <button>낮음</button><button data-on>보통</button><button>하이퍼</button>
                  </div>
                </div>
                <div className="left-links"><button>EDIT</button><button>일촌</button></div>
                <div className="wave"><span>파도타기</span>
                  <button aria-label="파도타기">▲</button></div>
                <dl className="room">
                  <div><dt>쓴 날</dt><dd>142일</dd></div>
                  <div><dt>남긴 것</dt><dd>1,284개</dd></div>
                  <div><dt>일촌</dt><dd>3명</dd></div>
                  <div><dt>집들이</dt><dd>25.9.20</dd></div>
                </dl>
              </div>
            </aside>

            <div className="rings">{[0,1,2,3].map(i => <span key={i} className="ring" />)}</div>

            <main className="page-right">
              <div className="right-head">
                <h1>다은님의 미니홈피</h1>
                <div className="acts"><button>꾸미기</button><button>로그아웃</button></div>
                <span className="url">/#/@daeun</span>
              </div>
              <div className="right-body"><Pane /></div>
            </main>
          </div>

          <nav className="tabs">
            {TABS.map(t => (
              <button key={t} className={`tab ${tab === t ? 'active' : ''}`} onClick={() => setTab(t)}>{t}</button>
            ))}
            <button className="tab add">+</button>
          </nav>
        </div>
      </div>

      <div className="dock">
        <button className="btn" onClick={() => setTab('홈')}>홈</button>
        <button className="btn ghost">일촌</button>
        <button className="btn ghost">꾸미기</button>
      </div>
    </div>
  )
}

createRoot(document.getElementById('root')!).render(<Preview />)
