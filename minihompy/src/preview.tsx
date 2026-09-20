import { useState } from 'react'
import { createRoot } from 'react-dom/client'
import './styles/app.css'

/**
 * 디자인 미리보기. 실제 앱과 같은 CSS·같은 마크업을 쓰되 데이터만 가짜다.
 * Supabase를 붙이기 전에 모양을 확정하려고 둔다.
 */

const TABS = ['홈', '오늘', '달력', '다이어리', '사진첩', '가계부', '챌린지', '쥬크박스', '보관함', '방명록']
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
          <li><button className="tick" /><span className="what">과제 개요 1장 쓰기</span><span className="dday now">오늘</span></li>
          <li><button className="tick" /><span className="what">병원 예약 전화</span><span className="dday past">2일 지남</span></li>
          <li><button className="tick" /><span className="what">빨래 돌리기</span></li>
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
  return (
    <div>
      <div className="sec-title">오늘<span style={{ float: 'right', fontWeight: 400, color: '#b0b0b0' }}>7개 남음</span></div>
      <div className="quick-add">
        <input type="text" placeholder="할 일 한 줄" />
        <input type="date" style={{ width: 126 }} />
        <button className="btn">담기</button>
      </div>
      <ul className="checklist">
        <li><button className="tick" /><span className="what">교양 레포트 제출</span><span className="dday now">오늘</span><button className="x">×</button></li>
        <li><button className="tick" /><span className="what">병원 예약 전화</span><span className="dday past">2일 지남</span><button className="x">×</button></li>
        <li><button className="tick" /><span className="what">동아리 회비 보내기</span><span className="dday soon">D-3</span><button className="x">×</button></li>
        <li><button className="tick" /><span className="what">빨래 돌리기</span><button className="x">×</button></li>
        <li><button className="tick" /><span className="what">책 반납</span><span className="dday soon">D-5</span><button className="x">×</button></li>
      </ul>
      <div style={{ marginTop: 14 }}>
        <button className="fold">▸ 끝낸 것 12</button>
      </div>
    </div>
  )
}

function Cal() {
  const WEEK = ['일', '월', '화', '수', '목', '금', '토']
  const marks: Record<number, number> = { 3: 1, 8: 2, 12: 1, 15: 3, 20: 2, 22: 1, 27: 1 }
  return (
    <div>
      <div className="sec-title cal-head">
        <button className="nav">‹</button><span>2026년 9월</span><button className="nav">›</button>
      </div>
      <div className="cal-grid">
        {WEEK.map((w, i) => <div key={w} className="cal-wd" data-sun={i === 0} data-sat={i === 6}>{w}</div>)}
        {Array.from({ length: 42 }, (_, i) => {
          const day = i - 1
          const inMonth = day >= 1 && day <= 30
          return (
            <button key={i} className="cal-day" data-dim={!inMonth}
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
          <li><time>10:00</time><span className="what">팀플 회의</span><button className="x">×</button></li>
          <li><time>19:30</time><span className="what">엄마 생신 저녁</span><button className="x">×</button></li>
        </ul>
        <div className="quick-add">
          <input type="time" style={{ width: 96 }} /><input type="text" placeholder="무슨 일" />
          <button className="btn">담기</button>
        </div>
      </div>
    </div>
  )
}

function Money() {
  const cats: [string, number][] = [['식비', 182000], ['카페', 63000], ['교통', 44000], ['쇼핑', 39000], ['구독', 21500]]
  const spent = 349500, planned = 450000
  const pct = Math.round((spent / planned) * 100)
  return (
    <div>
      <div className="sec-title">가계부<span style={{ float: 'right', fontWeight: 400, color: '#b0b0b0' }}>9월</span></div>
      <div className="money-head">
        <div className="big"><span className="k">썼다</span><b>{won(spent)}</b></div>
        <div className="bar"><i style={{ width: `${pct}%` }} /></div>
        <div className="k">예산 {won(planned)} 중 {pct}% · {won(planned - spent)} 남음</div>
      </div>
      <div className="quick-add money">
        <input type="text" placeholder="금액" style={{ width: 92 }} />
        <select style={{ width: 88 }}><option>식비</option></select>
        <input type="text" placeholder="뭐에 썼나 (생략 가능)" />
        <label className="tiny"><input type="checkbox" style={{ width: 'auto' }} />예산</label>
        <button className="btn">담기</button>
      </div>
      <div className="cat-rows">
        {cats.map(([k, v]) => (
          <div key={k} className="cat-row">
            <span className="chip">{k}</span>
            <i style={{ width: `${Math.round((v / spent) * 100)}%` }} />
            <b>{won(v)}</b>
          </div>
        ))}
      </div>
      <ul className="ledger-list">
        <li><span className="chip">식비</span><span className="what">점심 김밥</span><b>{won(4500)}</b><span className="when">19일</span><button className="x">×</button></li>
        <li><span className="chip">카페</span><span className="what">아메리카노</span><b>{won(4800)}</b><span className="when">19일</span><button className="x">×</button></li>
        <li><span className="chip">교통</span><span className="what">지하철</span><b>{won(2800)}</b><span className="when">18일</span><button className="x">×</button></li>
      </ul>
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
      <div className="sec-title">방명록 <span style={{ color: '#b0b0b0', fontWeight: 400 }}>3</span></div>
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


const PHOTOS = [
  ['#f3c9d4','한강 노을'], ['#cfe0f5','고양이'], ['#d9eede','카페'],
  ['#f6e3c5','생일'], ['#e0d6f2','비 오는 날'], ['#f9d7c9','바다'],
]

function Dia() {
  const days: [number, string, string, string, string][] = [
    [20, '9월', '금', '🌷 행복', '오늘 과제 겨우 냈다. 끝나고 먹은 아이스크림이 제일 맛있었음.\n내일은 좀 쉬어야지.'],
    [19, '9월', '목', '☁️ 그냥그럼', '커피 두 잔이나 마셨다. 잠이 안 온다.'],
    [17, '9월', '화', '🌟 뿌듯', '3주 미루던 병원 예약 드디어 했다.'],
  ]
  return (
    <div>
      <div className="sec-title">다이어리<span style={{ float: 'right', fontWeight: 400, color: '#b0b0b0' }}>31일</span></div>
      <button className="diary-open">✎ 오늘 쓰기</button>
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

function Pics() {
  return (
    <div>
      <div className="sec-title">사진첩<span style={{ float: 'right', fontWeight: 400, color: '#b0b0b0' }}>64장</span></div>
      <button className="photo-drop">＋ 사진 올리기</button>
      <div className="polaroids">
        {PHOTOS.map(([c, cap], i) => (
          <figure key={cap} style={{ '--tilt': `${(i % 5) - 2}deg` } as React.CSSProperties}>
            <div style={{ width: '100%', aspectRatio: '1/1', background: c }} />
            <figcaption><span>{cap}</span></figcaption>
            <button className="pull">×</button>
          </figure>
        ))}
      </div>
    </div>
  )
}

function Juke() {
  const songs = ['좋은 날', 'Through the Night', '밤편지', '너의 의미', 'Spring Day']
  return (
    <div>
      <div className="sec-title">쥬크박스<span style={{ float: 'right', fontWeight: 400, color: '#b0b0b0' }}>5곡</span></div>
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
            <button className="x">×</button>
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
      <div className="sec-title">보관함<span style={{ float: 'right', fontWeight: 400, color: '#b0b0b0' }}>5장</span></div>
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
              <select defaultValue=""><option value="">어디로 →</option></select>
              <button className="x">×</button>
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}

const PANES: Record<string, () => JSX.Element> = {
  홈: Home, 오늘: Todo, 달력: Cal, 가계부: Money, 챌린지: Ch, 방명록: Guest,
  다이어리: Dia, 사진첩: Pics, 쥬크박스: Juke, 보관함: Box,
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
            <div className="page-left">
              <div className="counter">TODAY <b>12</b> | TOTAL <span className="total">3,481</span></div>
              <div className="left-card">
                <div className="minimi"><span className="empty">프사<br />없음</span>
                  <button className="upload">사진 바꾸기</button></div>
                <div className="left-head-text">
                  <div className="home-name">다은님의 미니홈피</div>
                  <div className="home-tagline">오늘도 어떻게든</div>
                  <div className="mood-row"><span className="label">TODAY IS..</span>
                    <select defaultValue="그냥그럼"><option>그냥그럼</option></select></div>
                  <div className="energy">
                    <button>낮음</button><button data-on>보통</button><button>하이퍼</button>
                  </div>
                </div>
                <div className="left-links"><button>EDIT</button><button>일촌</button></div>
                <div className="wave"><span>파도타기</span><button>▲</button></div>
              </div>
            </div>

            <div className="rings">{[0,1,2,3].map(i => <span key={i} className="ring" />)}</div>

            <div className="page-right">
              <div className="right-head">
                <h1>다은님의 미니홈피</h1>
                <div className="acts"><button>꾸미기</button><button>로그아웃</button></div>
                <span className="url">/#/@daeun</span>
              </div>
              <div className="right-body"><Pane /></div>
            </div>
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
