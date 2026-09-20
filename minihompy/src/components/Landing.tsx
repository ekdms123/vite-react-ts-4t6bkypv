/** 로그인 전 화면. 설명을 길게 하지 않는다. */
export default function Landing({ onSignIn }: { onSignIn: () => void }) {
  return (
    <div className="stage">
      <div className="binder-wrap" style={{ maxWidth: 420, paddingRight: 0 }}>
        <div className="binder">
          <div style={{ padding: '34px 26px', textAlign: 'center' }}>
            <div className="home-name" style={{ fontSize: 17 }}>미니홈피</div>
            <p className="k soft" style={{ lineHeight: 1.9, padding: '14px 0 22px' }}>
              오늘 할 일, 달력, 일기, 가계부, 챌린지.<br />
              한 집에 다 있고, 방명록도 있다.
            </p>
            <button className="btn" style={{ padding: '10px 20px' }} onClick={onSignIn}>
              구글로 시작하기
            </button>
            <p className="k soft" style={{ paddingTop: 16, fontSize: 10 }}>
              로그인하면 내 집이 하나 생긴다.
            </p>
          </div>
        </div>
      </div>
    </div>
  )
}
